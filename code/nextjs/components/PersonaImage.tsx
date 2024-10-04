import ImageDto from "@/models/dto/ImageDto";
import PersonaDto from "@/models/dto/PersonaDto";

/**
 * Props for the PersonaImage component
 * @typedef {Object} PersonaImageProps
 * @property {ImageDto} image - The image data to display
 * @property {number} index - The index of the image in a list (if applicable)
 */
type PersonaImageProps = {
  image: ImageDto,
  index: number;
}

/**
 * PersonaImage component
 * Displays an image along with its associated information
 * 
 * @param {PersonaImageProps} props - The component props
 * @returns {JSX.Element} The rendered PersonaImage component
 */
const PersonaImage = ({ image, index }: PersonaImageProps) => {
  return (
    <div key={index}>
      {/* Display the image */}
      <img 
        className="h-auto max-w-full rounded-lg" 
        src={image.image_url} 
        alt={`Fetched Image ${index + 1}`} 
        style={{ width: '100%', height: 'auto' }} 
      />
      <div>
        {/* Display additional prompt if available */}
        {image.additional_prompt && (
          <p className="text-center mt-2 mb-2 text-lg font-normal text-gray-500 text-xl dark:text-gray-400">
            {image.additional_prompt}
          </p>
        )}
        {/* Display the motto */}
        <p className="italic text-center text-xl mb-2">
          {image.motto}
        </p>
        {/* Display the model used to create the image */}
        <p className="text-center text-xl text-gray-500">
          Created with {image.model === "openjourney" ? "OpenJourney" : "Dall-E"}
        </p>
      </div>
    </div>
  );
};

export default PersonaImage;