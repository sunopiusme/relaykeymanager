'use client';

import { useEffect, useState, useCallback } from 'react';
import type { TelegramWebApp, SafeAreaInset, TelegramUser } from '@/types/telegram';

interface UseTelegramReturn {
  webApp: TelegramWebApp | null;
  user: TelegramUser | null;
  isReady: boolean;
  isFullscreen: boolean;
  safeAreaInset: SafeAreaInset;
  contentSafeAreaInset: SafeAreaInset;
  platform: string;
  version: string;
  colorScheme: 'light' | 'dark';
  // Actions
  expand: () => void;
  close: () => void;
  requestFullscreen: () => void;
  exitFullscreen: () => void;
  setBackgroundColor: (color: string) => void;
  setHeaderColor: (color: string) => void;
  hapticFeedback: {
    impact: (style?: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
    notification: (type: 'error' | 'success' | 'warning') => void;
    selection: () => void;
  };
  showAlert: (message: string) => Promise<void>;
  showConfirm: (message: string) => Promise<boolean>;
}

const defaultSafeArea: SafeAreaInset = { top: 0, bottom: 0, left: 0, right: 0 };

export function useTelegram(): UseTelegramReturn {
  const [webApp, setWebApp] = useState<TelegramWebApp | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [safeAreaInset, setSafeAreaInset] = useState<SafeAreaInset>(defaultSafeArea);
  const [contentSafeAreaInset, setContentSafeAreaInset] = useState<SafeAreaInset>(defaultSafeArea);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const tg = window.Telegram?.WebApp;
    if (!tg) {
      setIsReady(true);
      return;
    }

    setWebApp(tg);
    setIsFullscreen(tg.isFullscreen ?? false);

    if (tg.safeAreaInset) {
      setSafeAreaInset(tg.safeAreaInset);
    }

    if (tg.contentSafeAreaInset) {
      setContentSafeAreaInset(tg.contentSafeAreaInset);
    }

    // Listen for events
    const handleSafeAreaChange = () => {
      if (tg.safeAreaInset) setSafeAreaInset(tg.safeAreaInset);
    };

    const handleContentSafeAreaChange = () => {
      if (tg.contentSafeAreaInset) setContentSafeAreaInset(tg.contentSafeAreaInset);
    };

    const handleFullscreenChange = () => {
      setIsFullscreen(tg.isFullscreen ?? false);
    };

    tg.onEvent('safeAreaChanged', handleSafeAreaChange);
    tg.onEvent('contentSafeAreaChanged', handleContentSafeAreaChange);
    tg.onEvent('fullscreenChanged', handleFullscreenChange);

    setIsReady(true);

    return () => {
      tg.offEvent('safeAreaChanged', handleSafeAreaChange);
      tg.offEvent('contentSafeAreaChanged', handleContentSafeAreaChange);
      tg.offEvent('fullscreenChanged', handleFullscreenChange);
    };
  }, []);

  const expand = useCallback(() => {
    webApp?.expand();
  }, [webApp]);

  const close = useCallback(() => {
    webApp?.close();
  }, [webApp]);

  const requestFullscreen = useCallback(() => {
    webApp?.requestFullscreen?.();
  }, [webApp]);

  const exitFullscreen = useCallback(() => {
    webApp?.exitFullscreen?.();
  }, [webApp]);

  const setBackgroundColor = useCallback((color: string) => {
    webApp?.setBackgroundColor(color);
  }, [webApp]);

  const setHeaderColor = useCallback((color: string) => {
    webApp?.setHeaderColor(color);
  }, [webApp]);

  const hapticFeedback = {
    impact: useCallback((style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft' = 'medium') => {
      webApp?.HapticFeedback?.impactOccurred(style);
    }, [webApp]),
    notification: useCallback((type: 'error' | 'success' | 'warning') => {
      webApp?.HapticFeedback?.notificationOccurred(type);
    }, [webApp]),
    selection: useCallback(() => {
      webApp?.HapticFeedback?.selectionChanged();
    }, [webApp]),
  };

  const showAlert = useCallback((message: string): Promise<void> => {
    return new Promise((resolve) => {
      if (webApp?.showAlert) {
        webApp.showAlert(message, () => resolve());
      } else {
        alert(message);
        resolve();
      }
    });
  }, [webApp]);

  const showConfirm = useCallback((message: string): Promise<boolean> => {
    return new Promise((resolve) => {
      if (webApp?.showConfirm) {
        webApp.showConfirm(message, (confirmed) => resolve(confirmed));
      } else {
        resolve(confirm(message));
      }
    });
  }, [webApp]);

  return {
    webApp,
    user: webApp?.initDataUnsafe?.user ?? null,
    isReady,
    isFullscreen,
    safeAreaInset,
    contentSafeAreaInset,
    platform: webApp?.platform ?? 'web',
    version: webApp?.version ?? '',
    colorScheme: webApp?.colorScheme ?? 'light',
    expand,
    close,
    requestFullscreen,
    exitFullscreen,
    setBackgroundColor,
    setHeaderColor,
    hapticFeedback,
    showAlert,
    showConfirm,
  };
}
