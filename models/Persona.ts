import { ObjectId } from "mongodb";

type Image = {
    generated_image_url: string;
    s3_location: string;
    model: string;
    additional_prompt: string;
    upvotes: number;
    downvotes: number;
};

class Persona {
    _id: ObjectId;
    name: string;
    images: Image[];

    constructor(_id: ObjectId, name: string, images: Image[]) {
        this._id = _id;
        this.name = name;
        this.images = images;
    }

    addImage(newImage: Image): void {
        this.images.push(newImage);
    }
}

export default Persona;