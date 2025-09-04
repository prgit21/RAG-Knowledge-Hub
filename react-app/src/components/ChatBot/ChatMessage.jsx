export default function ChatMessage({ message }) {
  return <div className={`chatbot-message ${message.role}`}>{message.text}</div>;
}
