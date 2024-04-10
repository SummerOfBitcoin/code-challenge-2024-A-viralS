

const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const { readFile, writeFile } = require('./utils/fileUtils');
const { validateTransaction } = require('./utils/transactionUtils');

function calculateTXID() {
    const mempool = path.join(__dirname, '..', 'mempool');

    const validTransactions = [];
  
    // Read and validate transactions from mempool
    const files = fs.readdirSync(mempool);
    const numFiles = files.length;
  
    for (const file of files) {
      const filePath = path.join(mempool, file);
      const transactionData = readFile(filePath);
      if (validateTransaction(transactionData)) {
        validTransactions.push(transactionData);
      }
    }
    console.log('first valid transaction:',validTransactions[0]);
    const { version, vin, vout, locktime } = validTransactions[0];
    const transactionData = `${version}${JSON.stringify(vin)}${JSON.stringify(vout)}${locktime}`;
    const txid = crypto.createHash('sha256').update(transactionData).digest('hex');
 console.log('txid:',txid);
 const fname = crypto.createHash('sha256').update(txid).digest('hex');
    console.log('fname:',fname);
  
  }
  calculateTXID();
 