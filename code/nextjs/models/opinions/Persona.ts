import Compass from "./Compass";

type Persona = {
  id: number;
  image_id: string;
  name: string;
  age: string;
  location: string;
  compasses: Compass[];
};

export default Persona;
