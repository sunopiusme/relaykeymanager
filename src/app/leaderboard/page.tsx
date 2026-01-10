'use client';

import { useEffect, useState } from 'react';
import { LeaderboardPage, LeaderboardPageSkeleton } from '@/components/LeaderboardPage';

export default function Leaderboard() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 800);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="fullscreen-container">
      {/* Skeleton */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        opacity: isLoading ? 1 : 0,
        pointerEvents: isLoading ? 'auto' : 'none',
        transition: 'opacity 0.3s ease',
        zIndex: isLoading ? 2 : 0,
      }}>
        <LeaderboardPageSkeleton />
      </div>

      {/* Content */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        opacity: isLoading ? 0 : 1,
        transition: 'opacity 0.3s ease',
        zIndex: isLoading ? 0 : 1,
      }}>
        <LeaderboardPage />
      </div>
    </div>
  );
}
