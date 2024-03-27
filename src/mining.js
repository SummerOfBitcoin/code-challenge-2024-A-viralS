const crypto = require('crypto');

function mineBlock(transactions, difficultyTarget) {

//calculate the merkle root

  if (transactions.length === 0) {
    return '';
  }

  let hashes = transactions.map(tx => crypto.createHash('sha256').update(JSON.stringify(tx)).digest('hex'));

  while (hashes.length > 1) {
    const newHashes = [];
    for (let i = 0; i < hashes.length; i += 2) {
      const left = hashes[i];
      const right = (i + 1) < hashes.length ? hashes[i + 1] : left;
      const combinedHash = crypto.createHash('sha256').update(left + right).digest('hex');
      newHashes.push(combinedHash);
    }
    hashes = newHashes;
  }

 const MerkleRoot=hashes[0];

  const blockHeader =`BLOCKHEADER: merkele root= ${MerkleRoot}'\n', nonce=${nonce}, target=${difficultyTarget}`;//block header contains: version, previous block hash, merkle root, timestamp, bits, and nonce
  const coinbaseTx = 'My Coinbase Transaction';

  // Serialize transactions
  const serializedTransactions = [coinbaseTx, ...transactions.flatMap(tx => tx.vin.map(input => input.txid))];
  //??are we sure that we have to write input.txid in this 

  // Find a valid nonce
  let nonce = 0;
  while (true) {
    const blockData = blockHeader + serializedTransactions.join('') + nonce;
    const blockHash = crypto.createHash('sha256').update(blockData).digest('hex');

    if (blockHash < difficultyTarget) {
      break;
    }

    nonce++;
    if (nonce % 1000000 === 0) {
      console.log(`Trying nonce: ${nonce}`);
    }
  }

  return { blockHeader, coinbaseTx, serializedTransactions, nonce };
}

module.exports = { mineBlock };