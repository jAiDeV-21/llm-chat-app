import React, { useState, useEffect } from "react";
import { chatAPI } from "../services/api";

export default function ProviderSelector({ onProviderChange }) {
  const [providers, setProviders] = useState({});
  const [selectedProvider, setSelectedProvider] = useState("anthropic");
  const [selectedModel, setSelectedModel] = useState("");
  
  useEffect(() => {
    loadProviders();
  }, []);
  
  const loadProviders = async () => {
    const data = await chatAPI.getAvailableProviders();
    setProviders(data);
    
    // Set default model
    if (data.anthropic?.length > 0) {
      setSelectedModel(data.anthropic[0]);
    }
  };
  
  const handleProviderChange = (e) => {
    const newProvider = e.target.value;
    setSelectedProvider(newProvider);
    
    // Auto-select first model of new provider
    const models = providers[newProvider] || [];
    if (models.length > 0) {
      setSelectedModel(models[0]);
    }
    
    onProviderChange(newProvider, selectedModel);
  };
  
  const handleModelChange = (e) => {
    const newModel = e.target.value;
    setSelectedModel(newModel);
    onProviderChange(selectedProvider, newModel);
  };
  
  return (
    <div className="provider-selector">
      <label>
        Provider:
        <select value={selectedProvider} onChange={handleProviderChange}>
          {Object.keys(providers).map(provider => (
            <option key={provider} value={provider}>
              {provider.charAt(0).toUpperCase() + provider.slice(1)}
            </option>
          ))}
        </select>
      </label>
      
      <label>
        Model:
        <select value={selectedModel} onChange={handleModelChange}>
          {(providers[selectedProvider] || []).map(model => (
            <option key={model} value={model}>
              {model}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}