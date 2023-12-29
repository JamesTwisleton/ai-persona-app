type Image = {
    generated_image_url: string;
    s3_location: string;
    model: string;
    additional_prompt: string;
    upvotes: number;
    downvotes: number;
};

export default Image;