import {
  S3Client,
  PutObjectCommand,
  GetObjectCommand,
  PutObjectCommandInput,
  GetObjectCommandInput,
} from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import { v4 as uuidv4 } from "uuid";
import { Buffer } from "buffer";
import Persona from "@/models/Persona";
import PersonaDto from "@/models/dto/PersonaDto";

// Initialize S3 client with AWS credentials
const s3Client = new S3Client({
  region: "us-east-1",
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

/**
 * Fetches an image from a URL and uploads it to S3
 * @param {string} imageUrl - The URL of the image to fetch
 * @param {string} name - The name associated with the image (for logging purposes)
 * @param {string} model - The model used to generate the image (for logging purposes)
 * @returns {Promise<string>} The S3 key of the uploaded image
 */
export async function fetchAndUploadImage(
  imageUrl: string,
  name: string,
  model: string,
): Promise<string> {
  try {
    // Fetch the image using the native fetch API
    const response = await fetch(imageUrl);
    if (!response.ok) {
      throw new Error(`Failed to fetch image: ${response.statusText}`);
    }
    const buffer = await response.arrayBuffer();

    // Convert ArrayBuffer to Buffer for S3 upload
    const bufferForUpload = Buffer.from(buffer);

    // Prepare S3 upload parameters
    const uploadParameters: PutObjectCommandInput = {
      Bucket: process.env.S3_BUCKET_NAME!,
      Key: `persona-generations/${uuidv4()}`, // Generate a unique key for the image
      Body: bufferForUpload,
      // ContentType could be added here if known
    };

    console.log(
      `Uploading image generated using model: ${model} for name: ${name} with image URL: ${imageUrl}`,
    );
    const putObjectCommand = new PutObjectCommand(uploadParameters);
    await s3Client.send(putObjectCommand);

    return uploadParameters.Key as string;
  } catch (error) {
    console.error("Error fetching or uploading image:", error);
    throw error;
  }
}

/**
 * Fetches images for a persona from S3 and returns a PersonaDto
 * @param {Persona} persona - The persona object containing image information
 * @returns {Promise<PersonaDto>} A PersonaDto with pre-signed URLs for each image
 */
export async function fetchImagesForPersonaFromS3(
  persona: Persona,
): Promise<PersonaDto> {
  const mappedImages = await Promise.all(
    persona.images.map(async (image) => {
      const presignedUrl = await fetchImageFromS3(image.s3_location);

      return {
        image_url: presignedUrl,
        model: image.model,
        additional_prompt: image.additional_prompt,
        // TODO: change this to use underscores like the rest
        mottoTone: image.mottoTone,
        motto: image.motto,
        upvotes: image.upvotes,
        downvotes: image.downvotes,
      };
    }),
  );

  return new PersonaDto(persona.name, mappedImages);
}

/**
 * Generates a pre-signed URL for an image stored in S3
 * @param {string} location - The S3 key of the image
 * @returns {Promise<string>} A pre-signed URL for the image
 */
export async function fetchImageFromS3(location: string): Promise<string> {
  try {
    const getObjectParameters: GetObjectCommandInput = {
      Bucket: process.env.S3_BUCKET_NAME!,
      Key: location,
    };

    console.log(`Generating pre-signed URL for image at location: ${location}`);
    const getObjectCommand = new GetObjectCommand(getObjectParameters);

    // Generate a pre-signed URL with a 60-second expiration time
    const presignedUrl = await getSignedUrl(s3Client, getObjectCommand, {
      expiresIn: 60,
    });

    return presignedUrl;
  } catch (error) {
    console.error("Error generating pre-signed URL for image from S3:", error);
    throw error;
  }
}
