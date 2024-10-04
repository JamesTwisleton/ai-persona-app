"use client";
import React, { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { convertToHyphenatedLowercase } from '@/lib/strings';

// Define the structure of the form data
interface FormData {
    name: string;
    prompt: string;
    mottoTone: string;
    model: string;
    force?: boolean;
}

/**
 * CreatePersonaForm component
 * Renders a form for creating or updating a persona
 * 
 * @param {Object} props - Component props
 * @param {boolean} props.force - Whether to force creation of a new persona
 * @param {string} props.providedName - Pre-filled name for the persona
 */
const CreatePersonaForm = ({ force = false, providedName = '' }) => {
    // Initialize form data state
    const [formData, setFormData] = useState<FormData>({
        name: providedName,
        prompt: '',
        mottoTone: 'neutral',
        model: '',
        ...(force && { force: true })
    });
    const [isLoading, setIsLoading] = useState<boolean>(false);

    const router = useRouter();

    /**
     * Handle changes in form inputs
     * @param {React.ChangeEvent<HTMLInputElement | HTMLSelectElement>} e - Change event
     */
    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    /**
     * Handle form submission
     * @param {FormEvent<HTMLFormElement>} e - Form submit event
     */
    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            const response = await fetch('/api/p', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                const targetUrl = `/p/${convertToHyphenatedLowercase(formData.name)}`;
                // Check if the target URL is the same as the current URL
                if (window.location.pathname === targetUrl) {
                    // If it's the same, reload the page
                    window.location.reload();
                } else {
                    // Otherwise, navigate to the target URL
                    router.push(targetUrl);
                }
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            // TODO: Implement proper error handling (e.g., display error message to user)
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="max-w-lg mx-auto">
            <form onSubmit={handleSubmit}>
                {!force && (
                    <h2 className="text-4xl font-extrabold dark:text-white py-5">
                        Try out a new persona
                    </h2>
                )}
                {/* Name input field */}
                <div className="mb-4">
                    <label htmlFor="name" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Name
                    </label>
                    <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        placeholder="Enter your persona's name"
                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                        required
                    />
                </div>
                {/* Description input field */}
                <div className="mb-4">
                    <label htmlFor="prompt" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Description
                    </label>
                    <input
                        type="text"
                        id="prompt"
                        name="prompt"
                        value={formData.prompt}
                        onChange={handleChange}
                        placeholder="Describe this person (optional)"
                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    />
                </div>
                {/* Attitude select field */}
                <div className="mb-6">
                    <label htmlFor="mottoTone" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Attitude
                    </label>
                    <select
                        id="mottoTone"
                        name="mottoTone"
                        value={formData.mottoTone}
                        onChange={handleChange}
                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    >
                        <option value="neutral">Neutral</option>
                        <option value="sarcastic">Sarcastic</option>
                        <option value="comical">Comical</option>
                        <option value="sombre">Sombre</option>
                    </select>
                </div>
                {/* Model select field */}
                <div className="mb-6">
                    <label htmlFor="model" className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Model to use
                    </label>
                    <select
                        id="model"
                        name="model"
                        value={formData.model}
                        onChange={handleChange}
                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                        required
                    >
                        <option value="openjourney">OpenJourney</option>
                        <option value="dall-e">Dall-E</option>
                    </select>
                </div>
                {/* Submit button */}
                <button
                    type="submit"
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    disabled={isLoading}
                >
                    {force ? 'Create another' : 'Create'}
                </button>
            </form>
            {/* Loading indicator */}
            {isLoading && (
                <div role="status" className="max-w-lg mx-auto pt-10 flex justify-center">
                    <svg aria-hidden="true" className="w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor" />
                        <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill" />
                    </svg>
                    <span className="sr-only">Loading...</span>
                </div>
            )}
        </div>
    );
};

export default CreatePersonaForm;
