'use client';

import type { TelegramUser } from '@/types/telegram';

interface UserDetailsProps {
  user: TelegramUser | null;
  starsAmount: number;
  usdAmount: number;
}

export function UserDetails({ user }: UserDetailsProps) {
  const displayName = user?.first_name || 'You';
  const initials = user?.first_name?.[0]?.toUpperCase() || 'Y';

  return (
    <div style={{
      background: '#fff',
      borderRadius: 16,
      overflow: 'hidden',
    }}>
      {/* Payment method */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '16px',
        borderBottom: '0.5px solid rgba(0,0,0,0.08)',
      }}>
        <span style={{ fontSize: 16, color: '#8e8e93', letterSpacing: -0.2 }}>Pay with</span>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
        }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/telegram-stars.svg" alt="" width={20} height={20} />
          <span style={{ fontSize: 16, fontWeight: 500, color: '#1c1c1e', letterSpacing: -0.2 }}>Telegram Stars</span>
        </div>
      </div>

      {/* From */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '16px',
      }}>
        <span style={{ fontSize: 16, color: '#8e8e93', letterSpacing: -0.2 }}>From</span>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
        }}>
          <span style={{ fontSize: 16, fontWeight: 500, color: '#1c1c1e', letterSpacing: -0.2 }}>{displayName}</span>
          {user?.photo_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img 
              src={user.photo_url} 
              alt="" 
              width={24} 
              height={24}
              style={{ borderRadius: 12, objectFit: 'cover' }}
            />
          ) : (
            <div style={{
              width: 24,
              height: 24,
              borderRadius: 12,
              background: '#007AFF',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 12,
              fontWeight: 600,
              color: '#fff',
            }}>
              {initials}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
