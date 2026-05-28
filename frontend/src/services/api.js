const API_BASE = "http://localhost:8000/api";

export const chatAPI = {
  createConversation: async () => {
    const response = await fetch(`${API_BASE}/conversations/create`, {
      method: "POST"
    });
    return response.json();
  },
  
  listConversations: async () => {
    const response = await fetch(`${API_BASE}/conversations/list`);
    return response.json();
  },
  
  getMessages: async (conversationId) => {
    const response = await fetch(
      `${API_BASE}/conversations/${conversationId}/messages`
    );
    return response.json();
  },
  
  sendMessage: async (conversationId, message, sessionId) => {
    const response = await fetch(`${API_BASE}/chat/send-message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        conversation_id: conversationId,
        message: message,
        session_id: sessionId
      })
    });
    return response.json();
  },

  cancelConversation: async (conversationId) => {
    const response = await fetch(
      `${API_BASE}/conversations/${conversationId}/cancel`,
      { method: "POST" }
    );
    return response.json();
  }
};