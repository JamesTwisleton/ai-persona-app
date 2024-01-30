import ImageDto from "@/models/dto/ImageDto";
import PersonaDto from "@/models/dto/PersonaDto";

type PersonaImageProps = {
  image: ImageDto,
  index: number;
}

const PersonaImage = ({ image, index }: PersonaImageProps) => {
  return (
    <div key={index}>
      <img className="h-auto max-w-full rounded-lg" src={image.image_url} alt={`Fetched Image ${index + 1}`} style={{ width: '100%', height: 'auto' }} />
      <div>
        <p className="text-center mt-2 mb-2 text-lg font-normal text-gray-500 text-xl dark:text-gray-400">
          {image.additional_prompt ? image.additional_prompt : null}
        </p>
        <p className="italic text-center text-xl mb-2">
          {image.motto}
        </p>
        <p className="text-center text-xl text-gray-500">
          Created with {image.model === "openjourney" ? "OpenJourney" : "Dall-E"}
        </p>
      </div>
    </div>
  );
};

export default PersonaImage;