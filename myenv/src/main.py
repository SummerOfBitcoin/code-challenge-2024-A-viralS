import os
import struct
import hashlib
import ecdsa
from ecdsa.util import sigdecode_string
from utils.fileUtils import read_file, write_file, file_exists
from mining import mine_block, serialize_tx
from utils.transactionUtils import validate_transaction
from utils.p2phk import verify_transactions


def main():
    src_dir = os.path.dirname(__file__)

    # Navigate two directories up to reach the parent directory of myenv
    parent_dir = os.path.dirname(os.path.dirname(src_dir))

    # Construct the path to the mempool directory
    mempool_path = os.path.join(parent_dir, "mempool")
    valid_transactions = []

    # Read and validate transactions from mempool
    files = os.listdir(mempool_path)

    filename_to_check = (
        "7de645056d100ee9d175ec61a90acc3d67812f93a3dae605a94f4db0f7c2a153.json"
    )
    exists = filename_to_check in files

    print(f"File {filename_to_check} exists in mempool: {exists}")
    num_files = len(files)

    num_valid_transactions = 0  # Initialize the counter here
    for file in files:
        file_path = os.path.join(mempool_path, file)
        transaction_data = read_file(file_path)
        results, num_valid = verify_transactions(transaction_data)
        if any(results):
            valid_transactions.append(transaction_data)
            num_valid_transactions += num_valid  # Increment the counter
    print(f"Number of valid transactions: {len(valid_transactions)}")
    print(f"Number of valid transactions: {num_valid_transactions}")
    # Mine the block with valid transactions
    difficulty_target = (
        "0000ffff00000000000000000000000000000000000000000000000000000000"
    )
    mined_block = mine_block(valid_transactions, difficulty_target)

    # Get the block header from the mined block
    block_header = mined_block["block_header"]
    print("block_header", block_header.hex())
    nounce = mined_block["nonce"]
    print("nounce in main", nounce)

    # Serialize the coinbase transaction
    # coinbase_tx = mined_block["coinbase_tx"]
    # serialized_coinbase_tx = serialize_tx(coinbase_tx)

    # Extract txids from mined block
    txids = mined_block["txids"]
    reversed_txid = [txid[::-1] for txid in txids]
    # Write the block header to the output file
    # Write the block header, coinbase transaction, and transaction IDs to the output file
    output_path = os.path.join(parent_dir, "output.txt")
    with open(output_path, "w") as output_file:
        # Write the block header
        output_file.write(block_header.hex() + "\n")

        # Write the serialized coinbase transaction
        output_file.write("coinbase transaction" + "\n")

        # Write the transaction IDs (txids) of the transactions mined in the block
        for txid in reversed_txid:
            output_file.write(txid + "\n")

    print("Output file 'output.txt' generated successfully.")


if __name__ == "__main__":
    main()
