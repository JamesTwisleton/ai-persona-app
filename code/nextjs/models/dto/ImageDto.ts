/**
 * Represents the data transfer object for an image associated with a persona.
 */
type ImageDto = {
    /** The URL of the generated image */
    image_url: string;
    /** The AI model used for image generation (e.g., "openjourney" or "dall-e") */
    model: string;
    /** Additional prompt used for image generation */
    additional_prompt: string;
    /** The desired tone for the persona's motto */
    mottoTone: string;
    /** The generated motto for the persona */
    motto: string;
    /** The number of upvotes received for this image */
    upvotes: number;
    /** The number of downvotes received for this image */
    downvotes: number;
    /** The S3 location where the image is stored (optional) */
    s3_location?: string;
};

export default ImageDto;
