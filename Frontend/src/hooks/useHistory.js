import { useState, useCallback } from 'react';

const MAX_HISTORY = 20;

export const useHistory = () => {
  const [history, setHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('deepfake_history') || '[]');
    } catch {
      return [];
    }
  });

  const addEntry = useCallback((result) => {
    setHistory(prev => {
      const updated = [result, ...prev].slice(0, MAX_HISTORY);
      try { localStorage.setItem('deepfake_history', JSON.stringify(updated)); } catch {}
      return updated;
    });
  }, []);

  const clearHistory = useCallback(() => {
    setHistory([]);
    localStorage.removeItem('deepfake_history');
  }, []);

  return { history, addEntry, clearHistory };
};
