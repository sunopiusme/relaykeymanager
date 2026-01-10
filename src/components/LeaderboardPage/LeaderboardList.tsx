'use client';

import './LeaderboardList.css';

interface LeaderboardItem {
  id: number;
  name: string;
  username: string;
  amount: number;
  rank: number;
}

interface LeaderboardListProps {
  items: LeaderboardItem[];
  currentUserId: number;
}

function getRankDisplay(rank: number): { text: string; color: string } {
  switch (rank) {
    case 1: return { text: '🥇', color: '#1c1c1e' };
    case 2: return { text: '🥈', color: '#1c1c1e' };
    case 3: return { text: '🥉', color: '#1c1c1e' };
    default: return { text: `${rank}`, color: '#8e8e93' };
  }
}

export function LeaderboardList({ items, currentUserId }: LeaderboardListProps) {
  return (
    <div className="lb-list">
      {items.map((item, index) => {
        const isCurrentUser = item.id === currentUserId;
        const rank = getRankDisplay(item.rank);
        const isFirst = index === 0;
        const isLast = index === items.length - 1;
        
        return (
          <div 
            key={item.id} 
            className={`lb-item ${isCurrentUser ? 'lb-item--me' : ''} ${isFirst ? 'lb-item--first' : ''} ${isLast ? 'lb-item--last' : ''}`}
          >
            <span className="lb-item__rank" style={{ color: rank.color }}>
              {rank.text}
            </span>
            
            <div className="lb-item__content">
              <span className="lb-item__name">{item.name}</span>
              <span className="lb-item__amount">${item.amount.toFixed(2)}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
