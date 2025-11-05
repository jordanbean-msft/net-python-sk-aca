import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import "./Chat.css";

// Relative URL works for both local development and Azure Container Apps deployment
const API_URL = "/api/chat";

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [streamEnabled, setStreamEnabled] = useState(true);
  const inputRef = useRef(null);

  // Focus input after bot responds
  useEffect(() => {
    if (!loading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [loading]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMsg = { role: "user", content: input };
    const currentInput = input;
    setLoading(true);
    setInput("");

    try {
      // Build chat history from current messages (before the new user message)
      const history = {
        messages: messages.map(msg => ({
          role: msg.role,
          content: msg.content
        }))
      };

      if (streamEnabled) {
        // Add user message first
        setMessages((msgs) => [...msgs, userMsg]);

        console.log("Sending streaming request...");
        const response = await fetch(API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: currentInput,
            history: history,
            stream: true
          }),
        });

        console.log("Response received, content-type:", response.headers.get("content-type"));
        if (!response.ok) throw new Error("Network error");

        // Add placeholder for assistant response
        setMessages((msgs) => [...msgs, { role: "assistant", content: "" }]);

        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let accumulatedContent = "";

        console.log("Starting to read stream...");
        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            console.log("Stream complete");
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || "";

          for (const line of lines) {
            console.log("Received line:", line);
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              console.log("SSE data:", data);
              if (data === '[DONE]') {
                break;
              }
              if (data.startsWith('[ERROR:')) {
                throw new Error(data.slice(8, -1));
              }
              accumulatedContent += data;
              // Update the last message (assistant) in real-time
              setMessages((msgs) => {
                const newMsgs = [...msgs];
                newMsgs[newMsgs.length - 1] = { role: "assistant", content: accumulatedContent };
                return newMsgs;
              });
              // Small delay to allow React to render
              await new Promise(resolve => setTimeout(resolve, 0));
            }
          }
        }
      } else {
        // Non-streaming response - add user message first
        setMessages((msgs) => [...msgs, userMsg]);

        const response = await fetch(API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: currentInput,
            history: history,
            stream: false
          }),
        });

        if (!response.ok) throw new Error("Network error");
        const data = await response.json();
        setMessages((msgs) => [...msgs, { role: "assistant", content: data.response }]);
      }
    } catch (err) {
      setMessages((msgs) => [...msgs, { role: "system", content: "Error: " + err.message }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <h2 className="chat-title">AI Chat</h2>
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="empty-state">
            Start the conversation!
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`message-wrapper ${msg.role}`}>
            <div className={`message-bubble ${msg.role}`}>
              <strong>{msg.role === "user" ? "You" : msg.role === "assistant" ? "Bot" : "System"}:</strong>{" "}
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          </div>
        ))}
        {loading && <div className="typing-indicator">Bot is typing...</div>}
      </div>
      <form onSubmit={sendMessage} className="chat-form">
        <input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="chat-input"
          placeholder="Type your message..."
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="send-button"
        >
          Send
        </button>
      </form>
      <div className="streaming-toggle">
        <label>
          <input
            type="checkbox"
            checked={streamEnabled}
            onChange={(e) => setStreamEnabled(e.target.checked)}
            disabled={loading}
          />
          <span>Enable streaming</span>
        </label>
      </div>
    </div>
  );
}

export default Chat;
