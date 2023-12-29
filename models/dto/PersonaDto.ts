import ImageDto from "./ImageDto";

class PersonaDto {
    name: string;
    images: ImageDto[];

    constructor(name: string, images: ImageDto[]) {
        this.name = name;
        this.images = images;
    }
}

export default PersonaDto;