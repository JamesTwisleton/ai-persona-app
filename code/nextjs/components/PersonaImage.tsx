"use client";
import ImageDto from "@/models/dto/ImageDto";
import React, { useState } from 'react';

/**
 * Props for the PersonaImage component
 * @typedef {Object} PersonaImageProps
 * @property {ImageDto} name - The name of the persona
 * @property {ImageDto} image - The image data to display
 * @property {number} index - The index of the image in a list (if applicable)
 */
type PersonaImageProps = {
  name: string,
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
const PersonaImage = ({ name, image, index }: PersonaImageProps) => {

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [blueskySkeetSkeeted, setBlueskySkeetSkeeted] = useState<boolean>(false);
  const [blueskyUrl, setBlueskyUrl] = useState<string | null>(null);
  const [generatedSkeet, setGeneratedSkeet] = useState<string | null>(null);

  
  const generateBlueskySkeet = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/generate-bluesky-skeet', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({name, image}),
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedSkeet(data.generatedPost);
      } else {
        const errorData = await response.json();
        setBlueskyUrl(errorData.error || "Failed to create BlueSky post.");
      }
  } catch (error) {
      console.error(`Error creating BlueSky post for ${name}:`, error);
      // TODO: Implement proper error handling (e.g., display error message to user)
  } finally {
      setIsLoading(false);
  }

  }

  const postToBluesky = async () => {
    setBlueskySkeetSkeeted(true);
  //   setIsLoading(true);
  //   try {
  //     const response = await fetch('/api/generate-bluesky-skeet', {
  //         method: 'POST',
  //         headers: {
  //             'Content-Type': 'application/json',
  //         },
  //         body: JSON.stringify({name, image}),
  //     });

  //     if (response.ok) {
  //       const data = await response.json();
  //       setGeneratedSkeet(data.generatedPost);
  //     } else {
  //       const errorData = await response.json();
  //       setBlueskyUrl(errorData.error || "Failed to create BlueSky post.");
  //     }
  // } catch (error) {
  //     console.error(`Error creating BlueSky post for ${name}:`, error);
  //     // TODO: Implement proper error handling (e.g., display error message to user)
  // } finally {
  //     setIsLoading(false);
  // }

  }

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
        <p className="text-center text-xl text-gray-500 pb-2">
          Created with {image.model === "openjourney" ? "OpenJourney" : "Dall-E"}
        </p>
        <button
          type="submit"
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          disabled={isLoading}
          onClick={() => generateBlueskySkeet()}
        >
          Generate BlueSky post by {name}
        </button>
            {generatedSkeet && (
          <p className="text-center text-green-600 mt-4">
            {generatedSkeet}
          </p>
        )}
        {isLoading && (
                <div role="status" className="max-w-lg mx-auto pt-10 flex justify-center">
                  {/* TODO: extact this svg somewhere else */}
                    <svg aria-hidden="true" className="w-8 h-8 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor" />
                        <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill" />
                    </svg>
                    <span className="sr-only">Loading...</span>
                </div>
            )}
            {generatedSkeet && (
          <button
          type="submit"
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 mt-2"
          disabled={blueskySkeetSkeeted}
          onClick={() => postToBluesky()}
        >
          Post to BlueSky
        </button>
        )}
      </div>
    </div>
  );
};

export default PersonaImage;