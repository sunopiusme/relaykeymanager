'use client';

import { useEffect, useState } from 'react';
import { useTelegram } from '@/hooks/useTelegram';
import { LeaderboardHeader } from './LeaderboardHeader';
import { LeaderboardList } from './LeaderboardList';
import { LeaderboardProgress } from './LeaderboardProgress';
import { CurrentUserIsland } from './CurrentUserIsland';
import './LeaderboardPage.css';

interface LeaderboardItem {
  id: number;
  name: string;
  username: string;
  amount: number;
  rank: number;
  photoUrl?: string;
}

interface LeaderboardData {
  leaderboard: LeaderboardItem[];
  stats: {
    total_stars: number;
    total_usd: number;
    total_donors: number;
    goal_stars: number;
    goal_usd: number;
  };
  currentUser?: LeaderboardItem;
}

export function LeaderboardPage() {
  const { user, contentSafeAreaInset, safeAreaInset } = useTelegram();
  const [data, setData] = useState<LeaderboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchLeaderboard() {
      try {
        const params = new URLSearchParams();
        if (user?.id) {
          params.set('userId', String(user.id));
        }
        
        const response = await fetch(`/api/leaderboard?${params.toString()}`);
        if (!response.ok) {
          throw new Error('Failed to fetch leaderboard');
        }
        
        const result = await response.json();
        setData(result);
      } catch (err) {
        console.error('Error fetching leaderboard:', err);
        setError('Failed to load leaderboard');
      }
    }

    fetchLeaderboard();
  }, [user?.id]);

  const topPadding = Math.max(contentSafeAreaInset.top, safeAreaInset.top, 8);
  const bottomPadding = Math.max(contentSafeAreaInset.bottom, safeAreaInset.bottom, 24);

  // Fallback data while loading
  const leaderboard = data?.leaderboard || [];
  const stats = data?.stats || {
    total_stars: 0,
    total_usd: 0,
    total_donors: 0,
    goal_stars: 50000,
    goal_usd: 1000,
  };

  // Current user data
  const currentUser = data?.currentUser || (user ? {
    id: user.id,
    name: `${user.first_name} ${user.last_name || ''}`.trim(),
    username: user.username || '',
    amount: 0,
    rank: 0,
    photoUrl: user.photo_url,
  } : null);

  if (error) {
    return (
      <div className="leaderboard-container" style={{ paddingTop: topPadding }}>
        <div className="leaderboard-error">
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="leaderboard-container"
      style={{
        paddingTop: topPadding,
        paddingBottom: bottomPadding + 88,
      }}
    >
      <div className="leaderboard-header-section">
        <LeaderboardHeader />
        <LeaderboardProgress 
          currentAmount={stats.total_usd} 
          goalAmount={stats.goal_usd} 
        />
      </div>
      
      <div className="leaderboard-list-section">
        <LeaderboardList 
          items={leaderboard} 
          currentUserId={currentUser?.id || 0}
        />
      </div>

      {currentUser && currentUser.rank > 0 && (
        <CurrentUserIsland 
          user={currentUser}
          bottomPadding={bottomPadding}
        />
      )}
    </div>
  );
}
