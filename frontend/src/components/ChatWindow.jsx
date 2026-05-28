
import React, { useState, useEffect } from "react";
import { chatAPI } from "../services/api";

export default function ChatWindow({ conversationId }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => generateSessionId());
  
  const handleSendMessage = async (text) => {
    setLoading(true);
    
    try {
      const response = await chatAPI.sendMessage(
        conversationId,
        text,
        sessionId
      );
      
      setMessages(prev => [
        ...prev,
        { role: "user", content: text },
        { role: "assistant", content: response.assistant_message }
      ]);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCancel = async () => {
    await chatAPI.cancelConversation(conversationId);
    setMessages([]);
  };
  
  const handleStream = async (text) => {
    setLoading(true);
    
    const eventSource = new EventSource(
      `/api/chat/send-message-stream?conversation_id=${conversationId}&session_id=${sessionId}`
    );
    
    let fullResponse = "";
    
    eventSource.onmessage = (event) => {
      const { chunk } = JSON.parse(event.data);
      fullResponse += chunk;
      
      setMessages(prev => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage?.role === "assistant") {
          lastMessage.content = fullResponse;
        }
        return newMessages;
      });
    };
    
    eventSource.onerror = () => {
      eventSource.close();
      setLoading(false);
    };
  };
  
  return (
    <div className="chat-window">
      <div className="actions">
        <button onClick={handleCancel}>Cancel Conversation</button>
      </div>
      {/* Rest of component */}
    </div>
  );
}
