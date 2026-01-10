'use client';

import Image from 'next/image';
import './CurrentUserIsland.css';

interface CurrentUserIslandProps {
  user: {
    id: number;
    name: string;
    username: string;
    amount: number;
    rank: number;
    photoUrl?: string;
  };
  bottomPadding: number;
}

export function CurrentUserIsland({ user, bottomPadding }: CurrentUserIslandProps) {
  const initials = user.name.charAt(0).toUpperCase();

  return (
    <div 
      className="user-island"
      style={{ paddingBottom: bottomPadding }}
    >
      <div className="island-content">
        <div className="island-rank">
          #{user.rank}
        </div>
        
        <div className="island-avatar">
          {user.photoUrl ? (
            <Image
              src={user.photoUrl}
              alt={user.name}
              width={44}
              height={44}
              className="island-avatar__img"
              unoptimized
            />
          ) : (
            initials
          )}
        </div>
        
        <div className="island-info">
          <span className="island-name">{user.name}</span>
          <span className="island-label">Your position</span>
        </div>
        
        <div className="island-amount-container">
          <span className="island-amount">${user.amount.toFixed(2)}</span>
          <span className="island-donated">donated</span>
        </div>
      </div>
    </div>
  );
}
