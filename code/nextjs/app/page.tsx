import CreatePersonaForm from "@/components/CreatePersonaForm"

export default function Home() {
  return (
    <div>
      <div className="p-10">
        <h1 className="text-center mb-4 text-4xl font-extrabold leading-none tracking-tight text-gray-900 md:text-5xl lg:text-6xl dark:text-white">
          Persona Composer
        </h1>
        <p className="text-center mb-3 text-2xl text-gray-500 dark:text-gray-400">
          Create social media personalities
        </p>
        <CreatePersonaForm />
      </div>
    </div>
  )
}
