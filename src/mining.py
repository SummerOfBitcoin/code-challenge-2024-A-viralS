import hashlib
import struct
import json 
import time

def serialize_tx(transaction):
    serialized = b""
    serialized += struct.pack("<L", transaction["version"])  # Version

    serialized += encode_varint(len(transaction["vin"]))  # Input count
    for inp in transaction["vin"]:
        txid_bytes = bytes.fromhex(inp["txid"])[::-1]  # TXID in little-endian format
        serialized += txid_bytes
        serialized += struct.pack("<L", inp["vout"])  # Output index
        scriptsig_bytes = bytes.fromhex(inp.get("scriptsig", ""))  # ScriptSig
        serialized += encode_varint(len(scriptsig_bytes))  # Script length
        serialized += scriptsig_bytes
        serialized += struct.pack("<L", inp["sequence"])  # Sequence

    serialized += encode_varint(len(transaction["vout"]))  # Output count
    for out in transaction["vout"]:
        serialized += struct.pack("<Q", out["value"])  # Output value
        scriptpubkey_bytes = bytes.fromhex(out["scriptpubkey"])  # ScriptPubKey
        serialized += encode_varint(len(scriptpubkey_bytes))  # ScriptPubKey size
        serialized += scriptpubkey_bytes

    serialized += struct.pack("<L", transaction["locktime"])  # Locktime
 
    txid = hashlib.sha256(hashlib.sha256(serialized).digest()).hexdigest()

    return txid


def serialize_block(block_data):
    return "|".join(map(str, block_data))


def calculate_merkle_root(transactions):
    if len(transactions) == 0:
        return ""

    hashes = [hashlib.sha256(json.dumps(tx).encode()).digest() for tx in transactions]

    while len(hashes) > 1:
        new_hashes = []
        for i in range(0, len(hashes), 2):
            left = hashes[i]
            right = hashes[i + 1] if i + 1 < len(hashes) else left
            combined_hash = hashlib.sha256(left + right).digest()
            new_hashes.append(combined_hash)
        hashes = new_hashes

    return hashes[0].hex()


    
def mine_block(transactions, difficulty_target):
    coinbase_tx = "My Coinbase Transaction"

    merkle_root = calculate_merkle_root(transactions)

    txids = [serialize_tx(tx) for tx in transactions]

    version = 1
    previous_block_hash = "00000000000000000397532e06a7601fb7a0d82e93a644c65d4b1ba011931dca"  # random hash example
    timestamp = int(time.time())
    bits = int(difficulty_target, 16)  # Convert difficulty target to integer
    nonce = 0

    # Format version as 4-byte little-endian
    version_bytes = version.to_bytes(4, byteorder='little')

    # Format previous_block_hash and merkle_root as natural byte order
    previous_block_hash_bytes = bytes.fromhex(previous_block_hash)[::-1]
    merkle_root_bytes = bytes.fromhex(merkle_root)[::-1]

    # Format timestamp, bits, and nonce as 4-byte little-endian
    timestamp_bytes = timestamp.to_bytes(4, byteorder='little')
    difficulty_target_int = int(difficulty_target, 16)
    difficulty_target_bytes = difficulty_target_int.to_bytes(32, byteorder='big')
    nonce_bytes = nonce.to_bytes(4, byteorder='little')

    block_header = {
        "version": version_bytes,
        "previous_block_hash": previous_block_hash_bytes,
        "merkle_root": merkle_root_bytes,
        "timestamp": timestamp_bytes,
        "bits": difficulty_target_bytes,
        "nonce": nonce_bytes
    }

    while True:
        block_data = [coinbase_tx] + txids + [str(nonce)]
        block_hash = hashlib.sha256(
            hashlib.sha256(serialize_block(block_header).encode() + "|".join(block_data).encode()).digest()
        ).hexdigest()

        if int(block_hash, 16) < bits:
            break

        nonce += 1
        if nonce % 1000000 == 0:
            print(f"Trying nonce: {nonce}")

    return {
        "block_header": block_header,
        "coinbase_tx": coinbase_tx,
        "txids": txids,
        "nonce": nonce,
        "merkle_root": merkle_root,
    }


def compact_size(value):
    if value < 0xfd:
        return value.to_bytes(1, 'little')
    elif value <= 0xffff:
        return b'\xfd' + value.to_bytes(2, 'little')
    elif value <= 0xffffffff:
        return b'\xfe' + value.to_bytes(4, 'little')
    else:
        return b'\xff' + value.to_bytes(8, 'little')
def encode_varint(n):
    if n < 0xFD:
        return struct.pack("<B", n)
    elif n <= 0xFFFF:
        return b"\xfd" + struct.pack("<H", n)
    elif n <= 0xFFFFFFFF:
        return b"\xfe" + struct.pack("<I", n)
    else:
        return b"\xff" + struct.pack("<Q", n)


# Example transaction

