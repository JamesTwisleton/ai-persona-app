/**
 * Represents an image associated with a persona.
 */
type Image = {
    /** The URL of the generated image */
    generated_image_url: string;
    /** The S3 storage location of the image */
    s3_location: string;
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
};

export default Image;