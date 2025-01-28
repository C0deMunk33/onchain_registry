const fetch = require('node-fetch');
const FormData = require('form-data');

const IPFS_API_URL = 'http://127.0.0.1:5001/api/v0';

async function uploadAndPin(jsonData) {
    try {
        const formData = new FormData();
        const jsonBuffer = Buffer.from(JSON.stringify(jsonData));
        formData.append('file', jsonBuffer, { filename: 'data.json', contentType: 'application/json' });
        
        const response = await fetch(`${IPFS_API_URL}/add`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        console.log(`Uploaded JSON and received CID: ${data.Hash}`);
        return data.Hash;
    } catch (error) {
        console.error(`Failed to upload JSON: ${error.message}`);
        return null;
    }
}

async function deleteAndUnpin(cid) {
    try {
        const response = await fetch(`${IPFS_API_URL}/pin/rm?arg=${cid}`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        console.log(`Unpinned CID: ${cid}`);
    } catch (error) {
        console.error(`Failed to unpin CID: ${error.message}`);
    }
}

async function getFile(cid) {
    try {
        const response = await fetch(`${IPFS_API_URL}/cat?arg=${cid}`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const jsonData = await response.json();
        console.log(`Retrieved JSON data:`, jsonData);
        return jsonData;
    } catch (error) {
        console.error(`Failed to retrieve JSON: ${error.message}`);
        return null;
    }
}

module.exports = {
    uploadAndPin,
    deleteAndUnpin,
    getFile
};

// Example usage
if (require.main === module) {
    const dataToUpload = {
        message: "Hello, IPFS!",
        timestamp: "2025-01-21",
        example: true
    };

    (async () => {
        try {
            const cid = await uploadAndPin(dataToUpload);
            if (cid) {
                const retrievedData = await getFile(cid);
                await deleteAndUnpin(cid);
            }
        } catch (error) {
            console.error(error);
        }
    })();
}