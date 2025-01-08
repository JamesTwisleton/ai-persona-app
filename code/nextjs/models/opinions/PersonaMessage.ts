import Message from "./Message";

type Persona = {
  uuid: string;
  name: string;
  age: number;
  location: string;
  profile_picture_filename: string;
  messages: Message[];
};

export default Persona;
