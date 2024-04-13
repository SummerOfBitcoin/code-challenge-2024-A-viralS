import os
import time
import hashlib
import json 
from utils.fileUtils import read_file, write_file, file_exists
from mining import mine_block


def main():
    mempool_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mempool')
    valid_transactions = []

    # Read and validate transactions from mempool
    files = os.listdir(mempool_path)
    filename_to_check = '7cd041411276a4b9d0ea004e6dd149f42cb09bd02ca5dda6851b3df068749b2d.json'
    exists = filename_to_check in files

    print(f"File {filename_to_check} exists in mempool: {exists}")
    num_files = len(files)

    for file in files:
        file_path = os.path.join(mempool_path, file)
        transaction_data = read_file(file_path)
        valid_transactions.append(transaction_data)

    # Mine the block with valid transactions
    difficulty_target = '0000ffff00000000000000000000000000000000000000000000000000000000'
    mined_block = mine_block(valid_transactions, difficulty_target)

    # Extract txids from mined block
    txids = mined_block['txids']

    # Write txids to output.txt
    output_path = os.path.join(os.path.dirname(__file__), 'output.txt')
    write_file(output_path, '\n'.join(txids) + '\n')

    print("Transaction IDs written to output.txt.")

if __name__ == "__main__":
    main()
