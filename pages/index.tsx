import React, { useState } from 'react';
import { useRouter } from 'next/router'; // Import useRouter
const IndexPage = () => {
  const [inputValue, setInputValue] = useState('');
  const [mode, setMode] = useState('');
  const router = useRouter(); // Initialize useRouter
  const handleSubmit = (event: { preventDefault: () => void; }) => {
    event.preventDefault();
    const formattedInput = encodeURIComponent(inputValue.replace(/ /g, '-'));
    const url = mode === 'dalle' ? `/create-image-from-name-dalle/${formattedInput}` : `/create-image-from-name-replicate/${formattedInput}`;
    router.push(url);
  };

  const handleInputChange = (event: { target: { value: React.SetStateAction<string>; }; }) => {
    setInputValue(event.target.value);
  };

  const handleModeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setMode(event.target.value);
  };

  return (
    <div>
      <h1>Enter a name to view or create a persona</h1>
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

export default IndexPage;
