import checkForExistingPersona from "@/lib/check-for-existing-persona";
import { prettifyUrlProvidedName } from "@/lib/strings";
import PersonaDto from "@/models/dto/PersonaDto";
import PersonaImage from "@/components/PersonaImage";
import CreatePersonaForm from "@/components/CreatePersonaForm";

export default async function Page({ params }: { params: { name: string } }) {

  const prettifiedName = prettifyUrlProvidedName(params.name);
  const maybeExistingPersona = await checkForExistingPersona(prettifiedName);
  if (maybeExistingPersona === false) {
    return <div>

      <div className="p-10">
        <h1 className="text-center mb-4 text-4xl font-extrabold leading-none tracking-tight text-gray-900 md:text-5xl lg:text-6xl dark:text-white">
          Persona Composer
        </h1>
        <p className="text-center mb-3 text-2xl text-gray-500 dark:text-gray-400">
          Create social media personalities
        </p>
        <h1 className="text-center text-2xl p-8">
          {prettifiedName} does not exist yet!
        </h1>
        <CreatePersonaForm providedName={prettifiedName} />
      </div>
    </div>;
  }

  const existingPersona = maybeExistingPersona as PersonaDto;

  return (
    <div>
      <div className="sticky top-0 bg-gray-950 p-4">
        <h1 className="mb-4 text-4xl font-extrabold leading-none tracking-tight text-gray-900 md:text-5xl lg:text-6xl dark:text-white">{prettifiedName}</h1>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3">
        <div className="col-span-1 p-2 p-4">
          <CreatePersonaForm force={true} providedName={prettifiedName} />
        </div>
        <div className="col-span-2 p-8">
        
        <h2 className="text-4xl font-extrabold dark:text-white">Here&apos;s what&apos;s been created for {prettifiedName} so far.</h2>
          <div className="grid grid-cols-1 md:grid-cols-1 lg:grid-cols-2 gap-4 bg-gray-950">
            {existingPersona.images.map((image, index) => (
              <PersonaImage key={image.image_url}image={image} index={index} />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}