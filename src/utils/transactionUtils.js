function validateTransaction(transactionData) {
    // Additional checks
    // 1. Validate ScriptPubKey Address Formats
    for (const output of transactionData.vout) {
        if (output.scriptpubkey_type === "v1_p2tr" && !output.scriptpubkey_address.startsWith("bc1")) {
            return false;
        } else if (output.scriptpubkey_type === "p2sh" && !output.scriptpubkey_address.startsWith("3")) {
            return false;
        }
    }

    // 2. Check Transaction Fee
    const totalOutputValue = transactionData.vout.reduce((acc, output) => acc + output.value, 0);
    const totalInputValue = transactionData.vin.reduce((acc, input) => {
        const prevOutput = input.prevout;
        return acc + (prevOutput ? prevOutput.value : 0);
    }, 0);
    const transactionFee = totalInputValue - totalOutputValue;
    if (transactionFee < 0) {
        return false; // Negative fee, invalid transaction
    }

    // 3. Confirm Coinbase Transaction Validation
    for (const input of transactionData.vin) {
        if (input.is_coinbase && input.prevout.value !== 0) {
            return false; // Invalid coinbase transaction
        }
    }

    // 4. Verify Locktime (if present)
    if (transactionData.locktime && transactionData.locktime < 0) {
        return false; // Invalid locktime
    }

    // 5. Check for Negative Values
    if (totalOutputValue < 0 || totalInputValue < 0) {
        return false; // Negative values, invalid transaction
    }

    // 6. Validate Witness Data
    for (const input of transactionData.vin) {
        if (!input.is_coinbase && (!input.witness || input.witness.length === 0)) {
            return false; // Witness data missing for non-coinbase transaction
        }
    }

    // Original validation checks
    // Check if the outputs are valid
    let totalOutput = 0;
    for (const output of transactionData.vout) {
        // Validate output values
        if (!output.scriptpubkey || !output.value || output.value < 0) {
            return false;
        }
        totalOutput += output.value;
    }

    // Check if the transaction version is valid
    const validVersion = [1, 2]; // Add more valid versions as needed
    if (!validVersion.includes(transactionData.version)) {
        return false;
    }

    // Calculate the total input value
    let totalInput = 0;
    for (const input of transactionData.vin) {
        // Validate input values
        if (!input.txid || input.vout === undefined || input.vout < 0) {
            return false;
        }

        // Get the value of the previous output being spent
        const prevOutput = input.prevout;
        if (!prevOutput || !prevOutput.value || prevOutput.value < 0) {
            return false;
        }
        totalInput += prevOutput.value;

        // Check if the input is a coinbase transaction and validate accordingly
        if (input.is_coinbase) {
            // Perform additional validation for coinbase transactions if needed
        }
    }

    // Check if the total output value is valid
    // The total output value should not be greater than the total input value
    if (totalOutput > totalInput) {
        return false;
    }

    // If all validation checks pass, return true
    return true;
}

module.exports = { validateTransaction };
