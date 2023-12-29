type ImageDto = {
    image_url: string;
    model: string;
    additional_prompt: string;
    upvotes: number;
    downvotes: number;
};

class PersonaDto {
    name: string;
    images: ImageDto[];

    constructor(name: string, images: ImageDto[]) {
        this.name = name;
        this.images = images;
    }
}

export default PersonaDto;