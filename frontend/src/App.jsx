
import React, { useState, useEffect } from "react";
import { chatAPI } from "./services/api";
import ChatWindow from "./components/ChatWindow";
import Sidebar from "./components/Sidebar";
import "./App.css";

function App() {
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  
  useEffect(() => {
    loadConversations();
  }, []);
  
  const loadConversations = async () => {
    const convos = await chatAPI.listConversations();
    setConversations(convos);
  };
  
  const handleNewChat = async () => {
    const newConvo = await chatAPI.createConversation();
    setConversations(prev => [newConvo, ...prev]);
    setActiveConversation(newConvo.id);
  };
  
  return (
    <div className="app">
      <Sidebar 
        conversations={conversations}
        activeId={activeConversation}
        onSelectConversation={setActiveConversation}
        onNewChat={handleNewChat}
      />
      {activeConversation && (
        <ChatWindow conversationId={activeConversation} />
      )}
    </div>
  );
}

export default App;
