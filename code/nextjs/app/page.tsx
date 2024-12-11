import CreatePersonaForm from "@/components/CreatePersonaForm";

/**
 * Home component - The main landing page of the Persona Composer application
 * @returns {JSX.Element} The rendered Home component
 */
export default function Home() {
  return (
    <div>
      {/* Main content container with padding */}
      <div className="p-10">
        {/* Main heading - Persona Composer */}
        <h1 className="text-center mb-4 text-4xl font-extrabold leading-none tracking-tight text-gray-900 md:text-5xl lg:text-6xl dark:text-white">
          Persona Composer
        </h1>
        {/* Subheading - Brief description of the application */}
        <p className="text-center mb-3 text-2xl text-gray-500 dark:text-gray-400">
          Create social media personalities
        </p>
        {/* Form component for creating new personas */}
        <CreatePersonaForm />
      </div>
    </div>
  );
}
