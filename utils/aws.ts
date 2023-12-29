// Import AWS SDK
const AWS = require('aws-sdk');
import Persona from '@/models/Persona';
import PersonaDto from '@/models/PersonaDto';
import { v4 as uuidv4 } from 'uuid';

// Configure AWS with your credentials
AWS.config.update({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: 'us-east-1'
});

// Create an S3 instance
const s3 = new AWS.S3();

const axios = require('axios');

export async function fetchAndUploadImage(imageUrl: string, name: string, model: string) {
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

export async function fetchImagesForPersonaFromS3(persona: Persona): Promise<PersonaDto> {
  const mappedImages = await Promise.all(persona.images.map(async (image) => {
    const presignedUrl = await fetchImageFromS3(image.s3_location);

    return {
      image_url: presignedUrl,
      model: image.model,
      additional_prompt: image.additional_prompt,
      upvotes: image.upvotes,
      downvotes: image.downvotes
    };
  }));

  return new PersonaDto(persona.name, mappedImages);
}

export async function fetchImageFromS3(location: string) {
  try {
    // Define S3 get parameters
    const getParams = {
      Bucket: process.env.S3_BUCKET_NAME,
      Key: location,
      Expires: 60 // URL expires in 60 seconds (or any duration suitable for your needs)
    };

    // Generate a pre-signed URL for temporary access
    console.log(`Generating pre-signed URL for image at location: ${location}`);
    const presignedUrl = s3.getSignedUrl('getObject', getParams);

    return presignedUrl;
  } catch (error) {
    console.error('Error generating pre-signed URL for image from S3:', error);
    throw error;
  }
}

