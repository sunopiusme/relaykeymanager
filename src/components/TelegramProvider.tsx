'use client';

import { useEffect, useState, type ReactNode } from 'react';

interface TelegramProviderProps {
  children: ReactNode;
}

export function TelegramProvider({ children }: TelegramProviderProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    
    const tg = window.Telegram?.WebApp;
    
    if (tg) {
      // Expand to full height first
      tg.expand();
      
      // Set background color to match our UI
      const bgColor = '#f2f2f7';
      tg.setBackgroundColor(bgColor);
      tg.setHeaderColor(bgColor);
      
      // Set bottom bar color if available (Bot API 7.10+)
      if (typeof tg.setBottomBarColor === 'function') {
        tg.setBottomBarColor(bgColor);
      }
      
      // Disable vertical swipes for better UX in fullscreen
      if (typeof tg.disableVerticalSwipes === 'function') {
        tg.disableVerticalSwipes();
      }

      // Request fullscreen mode (Bot API 8.0+)
      if (typeof tg.requestFullscreen === 'function') {
        tg.requestFullscreen();
      }
      
      // Signal that the app is ready
      tg.ready();
    }
  }, []);

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return null;
  }

  return <>{children}</>;
}
