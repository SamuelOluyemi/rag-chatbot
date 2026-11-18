import { useState } from "react";
import { askQuestion } from "../api";

export default function Chat() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);

  const sendQuestion = async () => {
    if (!question) return;

    const userMsg = { role: "user", text: question };
    setMessages((prev) => [...prev, userMsg]);

    const res = await askQuestion(question);

    const botMsg = { role: "bot", text: res.data.answer };
    setMessages((prev) => [...prev, botMsg]);

    setQuestion("");
  };

  return (
    <div className="card chat">
      <h2>Ask Questions</h2>

      <div className="chat-box">
        {messages.map((msg, i) => (
          <div key={i} className={msg.role}>
            {msg.text}
          </div>
        ))}
      </div>

      <div className="input-row">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask about your document..."
        />
        <button onClick={sendQuestion}>Send</button>
      </div>
    </div>
  );
}
