import { S3Client, PutObjectCommand, GetObjectCommand, PutObjectCommandInput, GetObjectCommandInput } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import { v4 as uuidv4 } from 'uuid';
import { Buffer } from 'buffer';
import Persona from '@/models/Persona';
import PersonaDto from '@/models/dto/PersonaDto';

const s3Client = new S3Client({
  region: 'us-east-1',
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!
  }
});

export async function fetchAndUploadImage(imageUrl: string, name: string, model: string): Promise<string> {
  try {
    // Use the native fetch API to get the image
    const response = await fetch(imageUrl);
    if (!response.ok) {
      throw new Error(`Failed to fetch image: ${response.statusText}`);
    }
    const buffer = await response.arrayBuffer();

    // Convert ArrayBuffer to Buffer for S3 upload
    const bufferForUpload = Buffer.from(buffer);

    const uploadParameters: PutObjectCommandInput = {
      Bucket: process.env.S3_BUCKET_NAME!,
      Key: `persona-generations/${uuidv4()}`,
      Body: bufferForUpload,
      // Additional parameters like ContentType can be added if necessary
    };

    console.log(`Uploading image generated using model: ${model} for name: ${name} with image URL: ${imageUrl}`);
    const putObjectCommand = new PutObjectCommand(uploadParameters);
    await s3Client.send(putObjectCommand);

    return uploadParameters.Key as string;
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
      mottoTone: image.mottoTone,
      motto: image.motto,
      upvotes: image.upvotes,
      downvotes: image.downvotes
    };
  }));

  return new PersonaDto(persona.name, mappedImages);
}

// Function to fetch an image from S3 using a pre-signed URL
export async function fetchImageFromS3(location: string): Promise<string> {
  try {
    const getObjectParameters: GetObjectCommandInput = {
      Bucket: process.env.S3_BUCKET_NAME!,
      Key: location
    };

    console.log(`Generating pre-signed URL for image at location: ${location}`);
    const getObjectCommand = new GetObjectCommand(getObjectParameters);

    // Generate a pre-signed URL with a specified expiration time
    const presignedUrl = await getSignedUrl(s3Client, getObjectCommand, { expiresIn: 60 }); // URL expires in 60 seconds

    return presignedUrl;
  } catch (error) {
    console.error('Error generating pre-signed URL for image from S3:', error);
    throw error;
  }
}
