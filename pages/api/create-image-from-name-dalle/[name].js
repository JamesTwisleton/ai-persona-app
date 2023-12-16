// pages/api/hello.js
import { Configuration, OpenAIApi } from "openai";
const configuration = new Configuration({
    apiKey: process.env.OPENAI_API_KEY,
});


export default async function handler(req, res) {
  const openai = new OpenAIApi(configuration);
  const { name } = req.query;
  const nameWithSpaces = name.replace(/-/g, ' ');
  const response = await openai.createImage({
    model: "dall-e-2",
    prompt: `Photorealistic social media profile photo of a person called ${nameWithSpaces} - Sigma 24mm f/8 — wider angle, smaller focal length`,
    n: 1,
    size: "256x256",
  });
  const image_url = response.data.data[0].url;
  res.status(200).json({ image_url: `${image_url}` });
}