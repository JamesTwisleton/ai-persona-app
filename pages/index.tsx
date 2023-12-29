import React, { useState, FormEvent } from 'react';
import ImageDto from '@/models/dto/ImageDto';

export default function Home() {
  const [name, setName] = useState<string>('');
  const [images, setImages] = useState<ImageDto[]>([]);
  const [model, setModel] = useState<string>('openjourney');
  const [prompt, setPrompt] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const fetchData = async (forceCreate = false) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/p`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, model, prompt, force: forceCreate }),
      });
      const data = await response.json();

      if (response.ok && data.images) {
        setName(data.name);
        setImages(data.images);
      } else {
        console.error('Error fetching data:', data);
      }
    } catch (error) {
      console.error('Fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    fetchData();
  };

  const handleForceCreate = async () => {
    await fetchData(true);
  };

  return (
    <div>

      <div style={{ position: 'fixed', top: 0, width: '100%', backgroundColor: '#fff', padding: '10px', textAlign: 'left'}}>
        <h2>{name || 'View or create a persona'}</h2>
      </div>
      <br></br>
      <br></br>
      <br></br>
      <br></br>
      <br></br>
      
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            What&apos;s their name?
            <br />
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </label>
        </div>
        <div>
          <label>
            Describe them (Optional):
            <br />
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
          </label>
        </div>
        <div>
          <label>Model to use:</label>
          <br />
          <label>
            OpenJourney
            <input
              type="radio"
              value="openjourney"
              checked={model === 'openjourney'}
              onChange={() => setModel('openjourney')}
            />
          </label>
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
        <button type="submit" disabled={loading}>
          {images.length > 0 ? 'Refresh' : loading? 'Loading...' : 'Reveal'}
        </button>
        {images.length > 0 && (
          <button type="button" onClick={handleForceCreate} disabled={loading}>
            {loading ? 'Loading...' : 'Create a new one'}
          </button>
        )}
      </form>
      <br></br>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px' }}>
        {images.map((image, index) => (
          <div key={index}>
            <img src={image.image_url} alt={`Fetched Image ${index + 1}`} style={{ width: '100%', height: 'auto' }} />
            <div>
              <p>Description: {image.additional_prompt || 'None'}</p>
              <p>Upvotes: {image.upvotes}</p>
              <p>Downvotes: {image.downvotes}</p>
              <p>Model: {image.model}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
