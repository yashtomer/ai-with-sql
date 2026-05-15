import React, { createContext, useContext, useState, useEffect } from 'react';

const ConfigContext = createContext();

export const ConfigProvider = ({ children }) => {
  const [llmConfig, setLlmConfig] = useState(() => {
    const savedConfig = localStorage.getItem('llmConfig');
    return savedConfig ? JSON.parse(savedConfig) : {
      provider: '',
      model: '',
      apiKey: ''
    };
  });

  useEffect(() => {
    localStorage.setItem('llmConfig', JSON.stringify(llmConfig));
  }, [llmConfig]);

  const updateConfig = (newConfig) => {
    setLlmConfig(newConfig);
  };

  const clearConfig = () => {
    setLlmConfig({
      provider: '',
      model: '',
      apiKey: ''
    });
  };

  return (
    <ConfigContext.Provider value={{ llmConfig, updateConfig, clearConfig }}>
      {children}
    </ConfigContext.Provider>
  );
};

export const useConfig = () => {
  const context = useContext(ConfigContext);
  if (!context) {
    throw new Error('useConfig must be used within a ConfigProvider');
  }
  return context;
};
