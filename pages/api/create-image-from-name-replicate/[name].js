// pages/api/hello.js
import Replicate from "replicate";
const replicate = new Replicate({
  auth: process.env.REPLICATE_API_TOKEN,
});



export default async function handler(req, res) {
  const { name } = req.query;
  const nameWithSpaces = name.replace(/-/g, ' ');

  const output = await replicate.run(
    "prompthero/openjourney:ad59ca21177f9e217b9075e7300cf6e14f7e5b4505b87b9689dbd866e9768969",
    {
      input: {
        prompt: `Photorealistic social media profile photo of a person called ${nameWithSpaces} - Sigma 24mm f/8 — wider angle, smaller focal length`
      }
    }
  );
  res.status(200).json({ image_url: `${output}` });
}