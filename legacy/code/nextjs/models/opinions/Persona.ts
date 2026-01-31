import Attribute from "./Attribute";

type Persona = {
  uuid: string;
  name: string;
  age: number;
  location: string;
  profile_picture_filename: string;
  attributes: Attribute[];
};

export default Persona;
