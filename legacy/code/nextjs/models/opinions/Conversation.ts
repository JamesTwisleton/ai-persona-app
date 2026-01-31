import PersonaMessage from "./PersonaMessage";
type Conversation = {
  uuid: string;
  topic: string;
  created: string;
  persona_messages: PersonaMessage[];
};

export default Conversation;
