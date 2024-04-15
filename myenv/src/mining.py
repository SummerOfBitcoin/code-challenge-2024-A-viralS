import hashlib
import struct
import json
import time

def get_compact(target):
    nSize = (target.bit_length() + 7) // 8
    nCompact = 0
    if nSize <= 3:
        nCompact = target << (8 * (3 - nSize))
    else:
        bn = target >> (8 * (nSize - 3))
        nCompact = bn

    # Check if the sign bit is set
    if nCompact & 0x00800000:
        nCompact >>= 8
        nSize += 1

    assert (nCompact & ~0x007FFFFF) == 0
    assert nSize < 256

    nCompact |= nSize << 24

    return nCompact

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
    txids = [serialize_tx(tx)[::-1] for tx in transactions]


    # Convert txids to little-endian byte buffers
    tx_buffers = [bytes.fromhex(tx)[::-1] for tx in txids]

    # 2-D array to save merkle tree and compute proof
    merkle_tree = [tx_buffers]

    while len(tx_buffers) > 1:
        merkle_leaves = []
        # Iterate over transactions, form pairs, and hash nodes
        for i in range(0, len(tx_buffers), 2):
            concatenated = tx_buffers[i] + (tx_buffers[i + 1] if i + 1 < len(tx_buffers) else tx_buffers[i])
            hashed = hashlib.sha256(hashlib.sha256(concatenated).digest()).digest()
            merkle_leaves.append(hashed)
        merkle_tree.append(merkle_leaves)
        tx_buffers = merkle_leaves

    return merkle_tree[-1][0].hex()


def mine_block(transactions, difficulty_target):
    coinbase_tx = "My Coinbase Transaction"

    merkle_root = calculate_merkle_root(transactions)
    print("merkle_root", merkle_root)

    txids = [serialize_tx(tx) for tx in transactions]

    version = 4

    previous_block_hash = "00000000000000000397532e06a7601fb7a0d82e93a644c65d4b1ba011931dca"  # random hash example
    timestamp = int(time.time())
    bits = int(difficulty_target, 16)  # Convert difficulty target to integer

    nonce = 0  # Initialize nonce here

    # Format version as 4-byte little-endian
    version_bytes = version.to_bytes(4, byteorder="little")

    # Format previous_block_hash and merkle_root as natural byte order
    previous_block_hash_bytes = bytes.fromhex(previous_block_hash)[::-1]
    merkle_root_bytes = (merkle_root)[::-1]
    print("merkle_root_bytes", merkle_root_bytes.hex())
    print("without hex ", merkle_root)

    # Format timestamp, bits, and nonce as 4-byte little-endian
    timestamp_bytes = timestamp.to_bytes(4, byteorder="little")

    compact_target = get_compact(bits)
    print("compact_target:", hex(compact_target))
    difficulty_target_bytes = compact_target.to_bytes(4, byteorder="little")

    # Initialize block header
    block_header = (
        version_bytes
        + previous_block_hash_bytes
        + merkle_root_bytes
        + timestamp_bytes
        + difficulty_target_bytes
        + nonce.to_bytes(4, byteorder="little")
    )
    print("bits", bits.to_bytes(32, byteorder="big").hex())
    while True:
        block_data = [coinbase_tx] + txids + [str(nonce)]
        block_header = (
            version_bytes
            + previous_block_hash_bytes
            + merkle_root_bytes
            + timestamp_bytes
            + difficulty_target_bytes
            + nonce.to_bytes(4, byteorder="little")
        )
        block_hash = (
            hashlib.sha256(hashlib.sha256(block_header).digest()).digest()[::-1].hex()
        )

        if (block_hash) < bits.to_bytes(32, byteorder="big").hex():
            break

        nonce += 1
        if nonce % 1000000 == 0:
            print(f"Trying nonce: {nonce}")

    # Update the nonce_bytes in the block_header after proof of work
    nonce_bytes = nonce.to_bytes(4, byteorder="little")
    print("nonce in mine_block", nonce)
    block_header = (
        version_bytes
        + previous_block_hash_bytes
        + merkle_root_bytes
        + timestamp_bytes
        + difficulty_target_bytes
        + nonce_bytes
    )
    print("block_header", block_header.hex())
    return {
        "block_header": block_header,
        "coinbase_tx": coinbase_tx,
        "txids": txids,
        "nonce": nonce,
        "merkle_root": merkle_root,
    }


def compact_size(value):
    if value < 0xFD:
        return value.to_bytes(1, "little")
    elif value <= 0xFFFF:
        return b"\xfd" + value.to_bytes(2, "little")
    elif value <= 0xFFFFFFFF:
        return b"\xfe" + value.to_bytes(4, "little")
    else:
        return b"\xff" + value.to_bytes(8, "little")


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
