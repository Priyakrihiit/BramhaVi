/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useCallback } from 'react';
import { api } from '../services/api';

export interface ChatMessage {
  sender: 'user' | 'vidya';
  text: string;
}

export function useVidyaChat() {
  const [chatLog, setChatLog] = useState<ChatMessage[]>([
    {
      sender: 'vidya',
      text: 'Hi! I am **Vidya**, your BrahmaVidya Galaxy AI companion. Ask me anything about programming, curriculum structure, or click on courses to generate interactive mock assessments!',
    },
  ]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const sendMessage = useCallback(async (messageText: string) => {
    if (!messageText.trim()) return;

    // Append user message
    setChatLog(prev => [...prev, { sender: 'user', text: messageText }]);
    setIsLoading(true);

    try {
      const res = await api.ai.chat(messageText);
      if (res.success && res.data) {
        setChatLog(prev => [...prev, { sender: 'vidya', text: res.data!.text }]);
      } else {
        setChatLog(prev => [
          ...prev,
          {
            sender: 'vidya',
            text: res.message || 'Apologies, I encountered an issue parsing your query.',
          },
        ]);
      }
    } catch (err) {
      setChatLog(prev => [
        ...prev,
        {
          sender: 'vidya',
          text: 'Network error communicating with Vidya AI. Please ensure your developer server is running.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearChat = useCallback(() => {
    setChatLog([
      {
        sender: 'vidya',
        text: 'System logs cleared. BrahmaVidya AI is ready to compile new responses.',
      },
    ]);
  }, []);

  return {
    chatLog,
    isLoading,
    sendMessage,
    clearChat,
  };
}
export default useVidyaChat;
