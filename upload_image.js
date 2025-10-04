const { createClient } = require('@sanity/client');
const fs = require('fs');

// Use the same client configuration as the website
const client = createClient({
    projectId: '4n33m7o6',
    dataset: 'production',
    apiVersion: '2024-05-01',
    useCdn: false, // Must be false to write
    token: process.env.SANITY_API_TOKEN,
});

const filePath = process.argv[2];
if (!filePath) {
    console.error('Error: Please provide a file path as an argument.');
    process.exit(1);
}

client.assets
    .upload('image', fs.createReadStream(filePath))
    .then(imageAsset => {
        // Output the asset document as JSON
        console.log(JSON.stringify(imageAsset));
    })
    .catch(error => {
        console.error('Error uploading image:', error.message);
        process.exit(1);
    });
