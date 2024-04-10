const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const { readFile, writeFile,fileExists } = require('./utils/fileUtils');
const { validateTransaction } = require('./utils/transactionUtils');
const { mineBlock } = require('./mining');

function main() {
  const mempool = 'mempool';
  const validTransactions = [];


  // Read and validate transactions from mempool
  const files = fs.readdirSync(mempool);
  const filenameToCheck = '70b1dafbd4edc721f342b2ae2d49a7c267cdd4391bae7b5382f3024f0e067232.json';
const exists = files.includes(filenameToCheck);

console.log(`File ${filenameToCheck} exists in mempool: ${exists}`);
  const numFiles = files.length;

  for (const file of files) {
    const filePath = path.join(mempool, file);
    const transactionData = readFile(filePath);
    if (validateTransaction(transactionData)) {
      validTransactions.push(transactionData);
    }
  }

  const numValidTransactions = validTransactions.length;
  console.log(`Number of files in mempool: ${numFiles}`);
  console.log(`Number of valid transactions: ${numValidTransactions}`);

  // Calculate the Merkle root
 
  // Mine the block with valid transactions
  const difficultyTarget = '0000ffff00000000000000000000000000000000000000000000000000000000';
  const { blockHeader, coinbaseTx, txids, nonce } = mineBlock(validTransactions, difficultyTarget);



  // Write output to output.txt
  const outputLines = [blockHeader,nonce, coinbaseTx, ...txids];
  writeFile('output.txt', outputLines.join('\n') + '\n');

  console.log(`Block mined with nonce: ${nonce}`);
}

main();