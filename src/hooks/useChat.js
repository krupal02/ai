import { useState, useCallback, useRef } from 'react';
import { initialMessages } from '../utils/mockData';

let messageIdCounter = initialMessages.length + 1;

function getTimeString() {
  const now = new Date();
  let hours = now.getHours();
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12 || 12;
  return `${hours}:${minutes} ${ampm}`;
}

export function useChat() {
  const [messages, setMessages] = useState(initialMessages);
  const [isTyping, setIsTyping] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState({});
  const scrollRef = useRef(null);

  const sendMessage = useCallback(async (text, userMode = 'first-time', coordinates = null, userProfile = null) => {
    if (!text.trim()) return;

    const userMsg = {
      id: messageIdCounter++,
      type: 'user',
      content: text.trim(),
      timestamp: getTimeString(),
    };

    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: text,
          user_profile: userMode,
          user_id: userProfile?.user_id || null,
          latitude: coordinates?.lat || null,
          longitude: coordinates?.lng || null
        })
      });

      const data = await res.json();

      const assistantMsg = {
        id: messageIdCounter++,
        type: 'assistant',
        content: data.response,
        timestamp: getTimeString(),
        hasNavigation: false,
        hasPlaces: false,
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, {
        id: messageIdCounter++,
        type: 'system',
        content: "Network error connecting to AI backend.",
        timestamp: getTimeString(),
      }]);
    } finally {
      setIsTyping(false);
    }
  }, []);

  const giveFeedback = useCallback((messageId, isPositive) => {
    setFeedbackGiven(prev => ({ ...prev, [messageId]: isPositive ? 'positive' : 'negative' }));
  }, []);

  return {
    messages,
    isTyping,
    feedbackGiven,
    sendMessage,
    giveFeedback,
    scrollRef,
  };
}
