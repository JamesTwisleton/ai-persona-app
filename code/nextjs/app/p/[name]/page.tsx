import checkForExistingPersona from "@/lib/check-for-existing-persona";
import { prettifyUrlProvidedName } from "@/lib/strings";
import PersonaDto from "@/models/dto/PersonaDto";
import PersonaImage from "@/components/PersonaImage";

export default async function Page({ params }: { params: { name: string } }) {

  const prettifiedName = prettifyUrlProvidedName(params.name);
  const maybeExistingPersona = await checkForExistingPersona(prettifiedName);
  if (maybeExistingPersona === false) {
    return <div><h1>{prettifiedName} does not exist yet!</h1></div>;
  }

  const existingPersona = maybeExistingPersona as PersonaDto;

  return (
    <div>
      <div className="sticky top-0 bg-gray-950 pb-1">
        <h1 className="mb-4 text-4xl font-extrabold leading-none tracking-tight text-gray-900 md:text-5xl lg:text-6xl dark:text-white">{prettifiedName}</h1>
        <p className="mb-3 text-gray-500 dark:text-gray-400">Here are all the previously created {prettifiedName}s. Create your own...?</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 bg-gray-950	">
        {existingPersona.images.map((image, index) => (
          <PersonaImage image={image} index={index} />
        ))}
      </div>
    </div>
  )
}