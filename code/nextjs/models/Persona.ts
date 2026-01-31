import { ObjectId } from "mongodb";
import Image from "./Image";

/**
 * Represents a Persona entity in the application.
 * A Persona is characterized by a unique identifier, a name, and a collection of associated images.
 */
class Persona {
  /** Unique identifier for the Persona */
  _id: ObjectId;
  /** Name of the Persona */
  name: string;
  /** Collection of images associated with the Persona */
  images: Image[];

  /**
   * Creates a new Persona instance.
   * @param _id - Unique identifier for the Persona
   * @param name - Name of the Persona
   * @param images - Initial collection of images associated with the Persona
   */
  constructor(_id: ObjectId, name: string, images: Image[]) {
    this._id = _id;
    this.name = name;
    this.images = images;
  }

  /**
   * Adds a new image to the Persona's collection of images.
   * @param newImage - The new Image to be added
   */
  addImage(newImage: Image): void {
    this.images.push(newImage);
  }

  /**
   * Retrieves the most recent image associated with the Persona.
   * @returns The most recently added Image, or undefined if no images exist.
   */
  getLatestImage(): Image | undefined {
    return this.images[this.images.length - 1];
  }
}

export default Persona;
