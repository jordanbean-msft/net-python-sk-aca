import React, { useState } from "react";

const API_URL = "/api/chat"; // Adjust if needed

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMsg = { role: "user", content: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setLoading(true);
    setInput("");
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
      if (!response.ok) throw new Error("Network error");
      const data = await response.json();
      setMessages((msgs) => [...msgs, { role: "assistant", content: data.response }]);
    } catch (err) {
      setMessages((msgs) => [...msgs, { role: "system", content: "Error: " + err.message }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 500, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h2>Chat</h2>
      <div style={{ border: "1px solid #ccc", padding: 16, minHeight: 200, marginBottom: 16 }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: 8 }}>
            <b>{msg.role === "user" ? "You" : msg.role === "assistant" ? "Bot" : "System"}:</b> {msg.content}
          </div>
        ))}
        {loading && <div>Bot is typing...</div>}
      </div>
      <form onSubmit={sendMessage} style={{ display: "flex" }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={{ flex: 1, padding: 8 }}
          placeholder="Type your message..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()} style={{ marginLeft: 8 }}>
          Send
        </button>
      </form>
    </div>
  );
}

export default Chat;
