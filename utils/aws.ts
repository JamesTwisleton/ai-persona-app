// Import AWS SDK
const AWS = require('aws-sdk');
import { v4 as uuidv4} from 'uuid';

// Configure AWS with your credentials
AWS.config.update({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: 'us-east-1'
});

// Create an S3 instance
const s3 = new AWS.S3();

const axios = require('axios');

export default async function fetchAndUploadImage(imageUrl: string, name: string, model: string) {
  try {
    // Fetch the image
    const response = await axios({
      method: 'get',
      url: imageUrl,
      responseType: 'arraybuffer'
    });

    // Define S3 upload parameters
    const uploadParams = {
      Bucket: process.env.S3_BUCKET_NAME,
      Key: `persona-generations/${uuidv4()}`,
      Body: response.data
    };

    // Upload to S3
    console.log(`Uploading image generated using model: ${model} for name: ${name} with image url: ${imageUrl}`)
    const s3Response = await s3.upload(uploadParams).promise();
    return s3Response.key;
  } catch (error) {
    console.error('Error fetching or uploading image:', error);
    throw error;
  }
}
