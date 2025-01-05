import Message from "./Message";
type Conversation = {
  id: string;
  topic: string;
  messages: Message[];
};

export default Conversation;
