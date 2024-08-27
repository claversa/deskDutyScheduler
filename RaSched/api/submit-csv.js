const { MongoClient } = require('mongodb');
const csvParser = require('csv-parser');

const uri = process.env.MONGODB_URI;
const client = new MongoClient(uri);

module.exports = async (req, res) => {
    if (req.method === 'POST') {
        const { csvData, userName } = req.body;

        let csvArray = [];
        csvParser(csvData, { delimiter: ',' })
            .on('data', (data) => csvArray.push(data))
            .on('end', async () => {
                try {
                    await client.connect();
                    const database = client.db('RA_Unavailabilities');
                    const collection = database.collection('unavailabilities');

                    await collection.insertOne({
                        userName: userName,
                        data: csvArray
                    });

                    res.status(200).json({ message: 'CSV data submitted successfully!' });
                } catch (error) {
                    console.error('Error:', error);
                    res.status(500).json({ error: 'Error submitting CSV data.' });
                } finally {
                    await client.close();
                }
            });
    } else {
        res.status(405).json({ error: 'Method not allowed' });
    }
};
