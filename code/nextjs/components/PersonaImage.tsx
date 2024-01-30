import ImageDto from "@/models/dto/ImageDto";
import PersonaDto from "@/models/dto/PersonaDto";

type PersonaImageProps = {
  image: ImageDto,
  index: number; 
}

const PersonaImage = ({image, index}: PersonaImageProps) => {
    return (
      <div key={index}>
               <img className="h-auto max-w-full rounded-lg" src={image.image_url} alt={`Fetched Image ${index + 1}`} style={{ width: '100%', height: 'auto' }} />
               <div>
                 <p>Description: {image.additional_prompt || 'None'}</p>
                 <p>mottoTone: {image.mottoTone || 'None'}</p>
                 <p>motto: {image.motto || 'None'}</p>
                 <p>Model used to generate: {image.model}</p>
               </div>
             </div>
    );
  };
  
  export default PersonaImage;