'use client';

import { useTelegram } from '@/hooks/useTelegram';
import './DonationPageSkeleton.css';
import './DonationPage.css';

export function DonationPageSkeleton() {
  const { contentSafeAreaInset, safeAreaInset } = useTelegram();

  const topPadding = Math.max(contentSafeAreaInset.top, safeAreaInset.top, 8) + 80;
  const bottomPadding = Math.max(contentSafeAreaInset.bottom, safeAreaInset.bottom, 24);

  return (
    <div className="donation-page-container">
      <div 
        className="donation-page-main"
        style={{
          paddingTop: topPadding,
          paddingBottom: bottomPadding,
        }}
      >
        {/* Content section */}
        <div className="donation-content">
          {/* Header - matches DonationHeader */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 0,
            paddingTop: 8,
            paddingBottom: 16,
          }}>
            <div 
              className="skeleton-bone" 
              style={{ 
                width: 100, 
                height: 100, 
                borderRadius: 25,
              }} 
            />
            <div 
              className="skeleton-bone" 
              style={{ 
                height: 16, 
                width: 40, 
                borderRadius: 8,
                marginTop: 4,
              }} 
            />
          </div>

          {/* Card - matches DonationCard */}
          <div style={{
            background: '#ffffff',
            borderRadius: 16,
            padding: 16,
            display: 'flex',
            alignItems: 'center',
            gap: 16,
          }}>
            <div 
              className="skeleton-bone" 
              style={{ 
                width: 52, 
                height: 52, 
                borderRadius: 14,
                flexShrink: 0,
              }} 
            />
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 4 }}>
              <div 
                className="skeleton-bone" 
                style={{ height: 17, width: 120, borderRadius: 8 }} 
              />
              <div 
                className="skeleton-bone" 
                style={{ height: 15, width: 160, borderRadius: 8 }} 
              />
            </div>
          </div>
        </div>

        {/* Details section */}
        <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* UserDetails card */}
          <div style={{
            background: '#ffffff',
            borderRadius: 16,
            overflow: 'hidden',
          }}>
            {/* Pay with row */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: 16,
              borderBottom: '0.5px solid rgba(0,0,0,0.08)',
            }}>
              <div className="skeleton-bone" style={{ height: 16, width: 56, borderRadius: 8 }} />
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div className="skeleton-bone" style={{ width: 20, height: 20, borderRadius: 10 }} />
                <div className="skeleton-bone" style={{ height: 16, width: 104, borderRadius: 8 }} />
              </div>
            </div>

            {/* From row */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: 16,
            }}>
              <div className="skeleton-bone" style={{ height: 16, width: 32, borderRadius: 8 }} />
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div className="skeleton-bone" style={{ height: 16, width: 48, borderRadius: 8 }} />
                <div className="skeleton-bone" style={{ width: 24, height: 24, borderRadius: 12 }} />
              </div>
            </div>
          </div>

          {/* Button */}
          <div>
            <div 
              className="skeleton-bone" 
              style={{ 
                width: '100%', 
                height: 56, 
                borderRadius: 28,
              }} 
            />
          </div>

          {/* Secured text */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <div className="skeleton-bone" style={{ height: 12, width: 96, borderRadius: 6 }} />
          </div>
        </div>
      </div>
    </div>
  );
}
