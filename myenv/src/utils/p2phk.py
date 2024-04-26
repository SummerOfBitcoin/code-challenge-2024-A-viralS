import hashlib
import struct
import ecdsa
from ecdsa.util import sigdecode_string


def parse_element(hex_str, offset, element_size):
    """
    Parses an element from a hex string.

    :param hex_str: The hex string to parse the element from.
    :type hex_str: str
    :param offset: The initial position of the object inside the hex string.
    :type offset: int
    :param element_size: The size of the element to extract.
    :type element_size: int
    :return: The extracted element from the provided string, and the updated offset after extracting it.
    :rtype: tuple[str, int]
    """
    return hex_str[offset : offset + element_size], offset + element_size


def dissect_signature(hex_sig):
    """
    Extracts the r, s, and ht components from a Bitcoin ECDSA signature.

    :param hex_sig: Signature in hex format.
    :type hex_sig: str
    :return: r, s, and ht components as a tuple.
    :rtype: tuple[str, str, str]
    """
    offset = 0
    # Check the sig contains at least the size and sequence marker
    assert len(hex_sig) > 4, "Wrong signature format."
    sequence, offset = parse_element(hex_sig, offset, 2)
    # Check sequence marker is correct
    assert sequence == "30", "Wrong sequence marker."
    signature_length, offset = parse_element(hex_sig, offset, 2)
    # Check the length of the remaining part matches the length of the signature + the length of the hashflag (1 byte)
    assert len(hex_sig[offset:]) / 2 == int(signature_length, 16) + 1, "Wrong length."
    # Get r
    marker, offset = parse_element(hex_sig, offset, 2)
    assert marker == "02", "Wrong r marker."
    len_r, offset = parse_element(hex_sig, offset, 2)
    len_r_int = int(len_r, 16) * 2  # Each byte represents 2 characters
    r, offset = parse_element(hex_sig, offset, len_r_int)
    # Get s
    marker, offset = parse_element(hex_sig, offset, 2)
    assert marker == "02", "Wrong s marker."
    len_s, offset = parse_element(hex_sig, offset, 2)
    len_s_int = int(len_s, 16) * 2  # Each byte represents 2 characters
    s, offset = parse_element(hex_sig, offset, len_s_int)
    # Get ht
    ht, offset = parse_element(hex_sig, offset, 2)
    assert offset == len(hex_sig), "Wrong parsing."

    return r, s, ht


def extract_public_key(transaction, input_idx):
    """
    Extracts the public key from the transaction's scriptsig if the scriptpubkey type is 'p2pkh'.

    :param transaction: The transaction dictionary.
    :type transaction: dict
    :param input_idx: Index of the input to extract the public key from.
    :type input_idx: int
    :return: The public key if found, otherwise None.
    :rtype: bytes or None
    """
    scriptsig = transaction["vin"][input_idx]["scriptsig_asm"]
    public_key = None
    if scriptsig:
        public_key_parts = scriptsig.split(" ")
        if len(public_key_parts) > 3:
            public_key = public_key_parts[3]
            if (
                public_key
                and transaction["vin"][input_idx]["prevout"]["scriptpubkey_type"]
                == "p2pkh"
            ):
                return bytes.fromhex(public_key)
    return None


def create_new_signature(transaction, input_idx):
    """
    Extracts the r, s values from the transaction's scriptSig and creates a new signature.

    :param transaction: The transaction dictionary.
    :type transaction: dict
    :param input_idx: Index of the input to create the new signature for.
    :type input_idx: int
    :return: The new signature.
    :rtype: bytes
    """
    # Extract scriptsig from transaction
    scriptsig = transaction["vin"][input_idx]["scriptsig_asm"]
    signature = scriptsig.split(" ")[1]

    # Dissect the signature
    r, s, _ = dissect_signature(signature)
    r = r[2:] if r.startswith("00") else r
    # Create new signature by concatenating r and s
    new_sig = bytes.fromhex(r) + bytes.fromhex(s)

    return new_sig


def encode_varint(n):
    if n < 0xFD:
        return struct.pack("<B", n)
    elif n <= 0xFFFF:
        return b"\xfd" + struct.pack("<H", n)
    elif n <= 0xFFFFFFFF:
        return b"\xfe" + struct.pack("<I", n)
    else:
        return b"\xff" + struct.pack("<Q", n)


def serialize_tx(transaction, input_idx=None):
    serialized = b""
    serialized += struct.pack("<L", transaction["version"])  # Version

    serialized += encode_varint(len(transaction["vin"]))  # Input count
    for idx, inp in enumerate(transaction["vin"]):
        input_serialized = b""
        txid_bytes = bytes.fromhex(inp["txid"])[::-1]  # TXID in little-endian format
        input_serialized += txid_bytes
        input_serialized += struct.pack("<L", inp["vout"])  # Output index
        prevout_scriptpubkey_bytes = bytes.fromhex(
            inp["prevout"]["scriptpubkey"]
        )  # ScriptPubKey of previous transaction
        if input_idx is not None and idx == input_idx:
            scriptsig_bytes = bytes.fromhex(inp["scriptsig"])
        else:
            scriptsig_bytes = b"\x00" * len(inp["scriptsig"])
        input_serialized += encode_varint(len(scriptsig_bytes))  # ScriptSig size
        input_serialized += scriptsig_bytes
        input_serialized += struct.pack("<L", inp["sequence"])  # Sequence
        serialized += input_serialized

    serialized += encode_varint(len(transaction["vout"]))  # Output count
    for out in transaction["vout"]:
        serialized += struct.pack("<Q", out["value"])  # Output value
        scriptpubkey_bytes = bytes.fromhex(out["scriptpubkey"])  # ScriptPubKey
        serialized += encode_varint(len(scriptpubkey_bytes))  # ScriptPubKey size
        serialized += scriptpubkey_bytes

    serialized += struct.pack("<L", transaction["locktime"])  # Locktime
    serialized += b"\x01\x00\x00\x00"  # SIGHASH_ALL
    txid = hashlib.sha256(hashlib.sha256(serialized).digest()).hexdigest()
    return serialized


def verify_transaction(transaction):
    """
    Verify if the transaction's signature is valid.

    :param transaction: The transaction dictionary.
    :type transaction: dict
    :return: Tuple containing list of boolean values indicating if the signatures are valid or not,
             and the number of valid signatures.
    :rtype: tuple[list[bool], int]
    """
    results = []
    num_valid = 0
    for input_idx, _ in enumerate(transaction["vin"]):
        transaction_serialized = serialize_tx(transaction, input_idx)
        message_hash = hashlib.sha256(
            hashlib.sha256(transaction_serialized).digest()
        ).hexdigest()
        public_key = extract_public_key(transaction, input_idx)
        if public_key is None:
            return False, 0
        new_signature = create_new_signature(transaction, input_idx)
        try:
            vk = ecdsa.VerifyingKey.from_string(public_key, curve=ecdsa.SECP256k1)
            if vk.verify_digest(
                new_signature, bytes.fromhex(message_hash), sigdecode=sigdecode_string
            ):
                results.append(True)
                num_valid += 1
            else:
                results.append(False)
        except:
            results.append(False)
    return results, num_valid


def verify_transactions(transactions):
    """
    Verify multiple transactions.

    :param transactions: List of transaction dictionaries.
    :type transactions: list[dict] or dict
    :return: List of boolean values indicating if the signatures are valid or not.
    :rtype: list[bool]
    """
    if isinstance(transactions, dict):
        transactions = [transactions]

    results = []
    num_valid = 0
    for transaction in transactions:
        # Check if the scriptsig is not empty and the scriptpubkey type is p2pkh
        scriptsig = transaction["vin"][0]["scriptsig_asm"]
        scriptpubkey_type = transaction["vin"][0]["prevout"]["scriptpubkey_type"]
        if scriptsig and scriptpubkey_type == "p2pkh":
            result = verify_transaction(transaction)
            if result:
                num_valid += 1
            results.append(result)
        else:
            results.append(False)
    return results, num_valid
