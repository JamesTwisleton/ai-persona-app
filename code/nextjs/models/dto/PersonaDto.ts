import ImageDto from './ImageDto';

/**
 * Represents a Data Transfer Object (DTO) for a Persona.
 * This class encapsulates the essential data of a persona, including its name and associated images.
 */
class PersonaDto {
  /** The name of the persona */
  name: string;

  /** An array of ImageDto objects representing the images associated with this persona */
  images: ImageDto[];

  /**
   * Constructs a new PersonaDto instance.
   * @param name The name of the persona.
   * @param images An array of ImageDto objects associated with the persona.
   */
  constructor(name: string, images: ImageDto[]) {
    this.name = name;
    this.images = images;
  }

  /**
   * Adds a new image to the persona's collection of images.
   * @param image The ImageDto object to be added.
   */
  addImage(image: ImageDto): void {
    this.images.push(image);
  }

  /**
   * Retrieves the most recent image associated with the persona.
   * @returns The most recently added ImageDto, or undefined if no images exist.
   */
  getLatestImage(): ImageDto | undefined {
    return this.images[this.images.length - 1];
  }
}

export default PersonaDto;
