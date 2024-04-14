import os
import struct
from utils.fileUtils import read_file, write_file, file_exists
from mining import mine_block, serialize_tx
from utils.transactionUtils import validate_transaction


def main():
    src_dir = os.path.dirname(__file__)

# Navigate one directory up to reach the parent directory
    parent_dir = os.path.dirname(src_dir)

# Construct the path to the mempool directory
    mempool_path = os.path.join(parent_dir, "mempool")
    valid_transactions = []

    # Read and validate transactions from mempool
    files = os.listdir(mempool_path)
    filename_to_check = (
        "60827e54145cd8eba8bd0db56eb74208ed483007e15aa2fec62f378ca170646f.json"
    )
    exists = filename_to_check in files

    print(f"File {filename_to_check} exists in mempool: {exists}")
    num_files = len(files)

    for file in files:
        file_path = os.path.join(mempool_path, file)
        transaction_data = read_file(file_path)
        if validate_transaction(transaction_data):  # Check if the transaction is valid
            valid_transactions.append(transaction_data)
    print(f"Number of valid transactions: {len(valid_transactions)}")
    # Mine the block with valid transactions
    difficulty_target = (
        "0000ffff00000000000000000000000000000000000000000000000000000000"
    )
    mined_block = mine_block(valid_transactions, difficulty_target)

    # Get the block header from the mined block
    block_header = mined_block["block_header"]
    print('block_header', block_header.hex())
    nounce = mined_block["nonce"]
    print('nounce in main', nounce)

    # Serialize the coinbase transaction
    # coinbase_tx = mined_block["coinbase_tx"]
    # serialized_coinbase_tx = serialize_tx(coinbase_tx)

    # Extract txids from mined block
    txids = mined_block["txids"]

    # Write the block header to the output file
    # Write the block header, coinbase transaction, and transaction IDs to the output file
    output_path = os.path.join(parent_dir, "output.txt")
    with open(output_path, "w") as output_file:
    # Write the block header
       output_file.write(block_header.hex() + "\n")

    # Write the serialized coinbase transaction
       output_file.write("coinbase transaction" + "\n")

    # Write the transaction IDs (txids) of the transactions mined in the block
       for txid in txids:
           output_file.write(txid + "\n")

print("Output file 'output.txt' generated successfully.")



# def serialize_block_header(block_header):
#     serialized_header = ""
#     for item in block_header:
#         if isinstance(item, int):
#             serialized_header += struct.pack("<L", item).hex()
#         else:
#             serialized_header += item
#     return serialized_header


if __name__ == "__main__":
    main()


# src_dir = os.path.dirname(__file__)

# # Navigate one directory up to reach the parent directory
# parent_dir = os.path.dirname(src_dir)

# # Construct the path to the mempool directory
# mempool_path = os.path.join(parent_dir, "mempool")