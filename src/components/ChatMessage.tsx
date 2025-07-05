
interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage = ({ message }: ChatMessageProps) => {
  return (
    <div
      className={`chat-bubble ${
        message.role === "user" ? "chat-bubble-user" : "chat-bubble-assistant"
      }`}
    >
      <p className="text-sm leading-relaxed">{message.content}</p>
      <p className="text-xs opacity-70 mt-2">
        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </p>
    </div>
  );
};
