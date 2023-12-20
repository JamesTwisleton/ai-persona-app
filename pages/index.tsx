// pages/index.tsx
import { useState } from 'react';

export default function Home() {
  const [name, setName] = useState('');
  const [imageURL, setImageURL] = useState('');
  const [model, setModel] = useState('openjourney');
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/p/${name}?model=${model}&prompt=${prompt}`);
      const data = await response.json();

      if (response.ok) {
        setImageURL(data.image_url);
      } else {
        // Handle error here if needed
        console.error('Error fetching data:', data);
      }
    } catch (error) {
      // Handle fetch error here
      console.error('Fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: { preventDefault: () => void; }) => {
    e.preventDefault();
    fetchData();
  };

  return (
    <div>
      <h1>Create a persona</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            What&apos;s their name?
            <br></br>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </label>
        </div>
        <br></br>
        <div>
          <label>
            (Optional) Describe them:
            <br></br>
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
          </label>
        </div>
        <br></br>
        <div>
          <label>
            OpenJourney
            <input
              type="radio"
              value="option1"
              checked={model === 'openjourney'}
              onChange={() => setModel('openjourney')}
            />
          </label>
          <br></br>
          <label>
            Dall-E
            <input
              type="radio"
              value="dall-e"
              checked={model === 'dall-e'}
              onChange={() => setModel('dall-e')}
            />
          </label>
        </div>
        <br></br>
        <div>
        <button type="submit" disabled={loading}>
            {loading ? 'Loading...' : 'Submit'}
          </button>
        </div>
      </form>
      {imageURL && (
        <div>
          <h2>Result:</h2>
          <img src={imageURL} alt="Fetched Image"/>
        </div>
      )}
    </div>
  );
}
