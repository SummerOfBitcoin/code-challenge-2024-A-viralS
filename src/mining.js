const crypto = require('crypto');

function calculateTXID(transaction) {
  const { version, vin, vout, locktime } = transaction;
  const transactionData = `${version}${JSON.stringify(vin)}${JSON.stringify(vout)}${locktime}`;
  const txid = crypto.createHash('sha256').update(transactionData).digest('hex');
  return txid;
}

function mineBlock(transactions, difficultyTarget) {
  const coinbaseTx = 'My Coinbase Transaction';

  // Calculate the Merkle root
  const merkleRoot = calculateMerkleRoot(transactions);

  // Calculate the transaction IDs (TXIDs)
  const txids = transactions.map(tx => calculateTXID(tx));

  // Populate the block header
  const version = 1;
  const previousBlockHash = 'PreviousBlockHash'; // Replace with actual previous block hash
  const timestamp = Math.floor(Date.now() / 1000);
  const blockHeader = `${version}|${previousBlockHash}|${timestamp}|${difficultyTarget}|${merkleRoot}|`;

  // Find a valid nonce
  let nonce = 0;
  while (true) {
    const blockData = `${blockHeader}|${coinbaseTx}|${txids.join('|')}|${nonce}`;
    const blockHash = crypto.createHash('sha256').update(blockData).digest('hex');

    if (parseInt(blockHash, 16) < parseInt(difficultyTarget, 16)) {
      break;
    }

    nonce++;
    if (nonce % 1000000 === 0) {
      console.log(`Trying nonce: ${nonce}`);
    }
  }

  console.log('merkleRoot:', merkleRoot);

  return { blockHeader, coinbaseTx, txids, nonce, merkleRoot };
}

module.exports = { mineBlock };

// Helper function to calculate the Merkle Root
function calculateMerkleRoot(transactions) {
  if (transactions.length === 0) {
    return '';
  }

  let hashes = transactions.map(tx => crypto.createHash('sha256').update(JSON.stringify(tx)).digest());

  while (hashes.length > 1) {
    const newHashes = [];
    for (let i = 0; i < hashes.length; i += 2) {
      const left = hashes[i];
      const right = (i + 1) < hashes.length ? hashes[i + 1] : left;
      const combinedHash = crypto.createHash('sha256').update(Buffer.concat([left, right])).digest();
      newHashes.push(combinedHash);
    }
    hashes = newHashes;
  }

  return hashes[0].toString('hex');
}
