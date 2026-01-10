'use client';

import './LeaderboardProgress.css';

interface LeaderboardProgressProps {
  currentAmount: number;
  goalAmount: number;
}

export function LeaderboardProgress({ currentAmount, goalAmount }: LeaderboardProgressProps) {
  const percentage = Math.min((currentAmount / goalAmount) * 100, 100);
  
  return (
    <div className="progress-card">
      <div className="progress-stats">
        <div className="progress-raised">
          <span className="progress-raised__value">
            ${currentAmount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </span>
          <span className="progress-raised__label">raised</span>
        </div>
        <div className="progress-goal">
          <span className="progress-goal__value">
            ${goalAmount.toLocaleString('en-US')}
          </span>
          <span className="progress-goal__label">goal</span>
        </div>
      </div>
      
      <div className="progress-track">
        <div 
          className="progress-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
