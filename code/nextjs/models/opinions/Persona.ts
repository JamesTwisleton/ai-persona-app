import Slider from "./Slider";

type Persona = {
  id: number;
  image_id: string;
  name: string;
  age: string;
  location: string;
  sliders: Slider[];
};

export default Persona;
