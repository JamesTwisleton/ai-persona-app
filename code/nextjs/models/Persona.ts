import { ObjectId } from "mongodb";
import Image from "./Image";
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