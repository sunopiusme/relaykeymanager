'use client';

import { useTelegram } from '@/hooks/useTelegram';
import './LeaderboardPageSkeleton.css';
import './LeaderboardPage.css';

export function LeaderboardPageSkeleton() {
  const { contentSafeAreaInset, safeAreaInset } = useTelegram();

  const topPadding = Math.max(contentSafeAreaInset.top, safeAreaInset.top, 8);
  const bottomPadding = Math.max(contentSafeAreaInset.bottom, safeAreaInset.bottom, 24);

  return (
    <div 
      className="leaderboard-container"
      style={{
        paddingTop: topPadding,
        paddingBottom: bottomPadding + 88,
      }}
    >
      <div className="leaderboard-header-section">
        {/* LeaderboardHeader */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 4,
          paddingTop: 8,
          paddingBottom: 16,
        }}>
          {/* Icon: 72x72, borderRadius 18 */}
          <div 
            className="skeleton-shimmer" 
            style={{ 
              width: 72, 
              height: 72, 
              borderRadius: 18,
            }} 
          />
          {/* Title: "Leaderboard" - fontSize 20 */}
          <div 
            className="skeleton-shimmer" 
            style={{ 
              width: 110, 
              height: 20, 
              borderRadius: 10,
              marginTop: 4,
            }} 
          />
          {/* Subtitle: "Top supporters of Relay" - fontSize 14 */}
          <div 
            className="skeleton-shimmer" 
            style={{ 
              width: 150, 
              height: 14, 
              borderRadius: 7,
            }} 
          />
        </div>

        {/* LeaderboardProgress */}
        <div style={{
          background: '#ffffff',
          borderRadius: 16,
          padding: 16,
          marginBottom: 8,
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            marginBottom: 12,
          }}>
            {/* Left: raised amount */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {/* $1,245.44 - fontSize 22 */}
              <div className="skeleton-shimmer" style={{ width: 95, height: 22, borderRadius: 11 }} />
              {/* "raised" - fontSize 13 */}
              <div className="skeleton-shimmer" style={{ width: 40, height: 13, borderRadius: 6 }} />
            </div>
            {/* Right: goal */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 2, alignItems: 'flex-end' }}>
              {/* $5,000 - fontSize 17 */}
              <div className="skeleton-shimmer" style={{ width: 55, height: 17, borderRadius: 8 }} />
              {/* "goal" - fontSize 13 */}
              <div className="skeleton-shimmer" style={{ width: 28, height: 13, borderRadius: 6 }} />
            </div>
          </div>
          {/* Progress bar: height 6 */}
          <div className="skeleton-shimmer" style={{ width: '100%', height: 6, borderRadius: 3 }} />
        </div>
      </div>

      {/* LeaderboardList */}
      <div className="leaderboard-list-section">
        <div style={{ background: '#ffffff', borderRadius: 16, overflow: 'hidden' }}>
          {[...Array(10)].map((_, i) => (
            <div 
              key={i}
              style={{
                display: 'flex',
                alignItems: 'center',
                padding: '14px 16px',
                gap: 14,
                borderBottom: i < 9 ? '0.5px solid rgba(60, 60, 67, 0.12)' : 'none',
              }}
            >
              {/* Rank: width 28, fontSize 15 */}
              <div className="skeleton-shimmer" style={{ width: 28, height: 15, borderRadius: 7 }} />
              {/* Content */}
              <div style={{ flex: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                {/* Name: fontSize 17 */}
                <div className="skeleton-shimmer" style={{ width: 80 + (i % 4) * 15, height: 17, borderRadius: 8 }} />
                {/* Amount: fontSize 17 */}
                <div className="skeleton-shimmer" style={{ width: 55, height: 17, borderRadius: 8 }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CurrentUserIsland */}
      <div style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        background: '#f2f2f7',
        padding: '8px 16px',
        paddingBottom: bottomPadding,
        zIndex: 10,
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          background: '#ffffff',
          borderRadius: 16,
          padding: '12px 16px',
        }}>
          {/* Rank badge: 36x36, borderRadius 10 */}
          <div className="skeleton-shimmer" style={{ width: 36, height: 36, borderRadius: 10, flexShrink: 0 }} />
          {/* Avatar: 44x44, borderRadius 50% */}
          <div className="skeleton-shimmer" style={{ width: 44, height: 44, borderRadius: 22, flexShrink: 0 }} />
          {/* Info */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2, minWidth: 0 }}>
            {/* Name: fontSize 16 */}
            <div className="skeleton-shimmer" style={{ width: 70, height: 16, borderRadius: 8 }} />
            {/* "Your position": fontSize 13 */}
            <div className="skeleton-shimmer" style={{ width: 85, height: 13, borderRadius: 6 }} />
          </div>
          {/* Amount container */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 2, flexShrink: 0 }}>
            {/* Amount: fontSize 17 */}
            <div className="skeleton-shimmer" style={{ width: 50, height: 17, borderRadius: 8 }} />
            {/* "donated": fontSize 12 */}
            <div className="skeleton-shimmer" style={{ width: 50, height: 12, borderRadius: 6 }} />
          </div>
        </div>
      </div>
    </div>
  );
}
