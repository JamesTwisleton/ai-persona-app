// pages/create-image-from-name/[name].js

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

const CreateImageFromName = () => {
  const router = useRouter();
  const { name } = router.query; // Extracting the dynamic segment 'name'
  const displayName = formatName(name);

  const [imageUrl, setImageUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [mode, setMode] = useState('');

  useEffect(() => {
    if (name) {
      fetchImage(name);
    }
  }, [name]);

  const fetchImage = async (name) => {
    setIsLoading(true);
    try {
      const url = `/api/create-image-from-name-dalle/${name}`;

      const response = await fetch(url);
      const data = await response.json();
      setImageUrl(data.image_url); // Assuming the API returns an object with a 'url' property
    } catch (error) {
      console.error('Error fetching image:', error);
    }
    setIsLoading(false);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const formattedInput = encodeURIComponent(inputValue.replace(/ /g, '-'));
    const url = mode === 'dalle' ? `/create-image-from-name-dalle/${formattedInput}` : `/create-image-from-name-replicate/${formattedInput}`;
    router.push(url);
  };

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleModeChange = (event) => {
    setMode(event.target.value);
  };

  return (
    <div>
      <h1>{displayName}</h1>
      {isLoading ? (
        <div>Loading...</div>
      ) : (
        imageUrl && <img src={imageUrl} alt={`Image for ${displayName}`} />
      )
      }
      <p>Refresh the page to regenerate</p>
      <h1>Try Another?</h1>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          value={inputValue} 
          onChange={handleInputChange} 
          placeholder="Enter a first and last name..." 
        />
        <div>
          <p>Select model:</p>
          <label>
            <input 
              type="radio" 
              value="replicate" 
              checked={mode === 'replicate'} 
              onChange={handleModeChange} 
            />
            OpenJourney
          </label>
          <br></br>
          <label>
            <input 
              type="radio" 
              value="dalle" 
              checked={mode === 'dalle'} 
              onChange={handleModeChange} 
            />
            DALL-E
          </label>
        </div>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

function formatName(str) {
    const nameWithSpaces = str ? str.replace(/-/g, ' ') : '';

    return nameWithSpaces
    .split('-')
    .map(segment => segment
      .split(/\s+/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ')
    )
    .join(' ');
  }

export default CreateImageFromName;
