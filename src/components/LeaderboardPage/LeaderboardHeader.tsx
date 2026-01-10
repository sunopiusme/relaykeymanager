'use client';

import Image from 'next/image';

export function LeaderboardHeader() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 4,
      paddingTop: 8,
      paddingBottom: 16,
    }}>
      <div style={{
        width: 72,
        height: 72,
        borderRadius: 18,
        overflow: 'hidden',
        background: '#e5e5ea',
      }}>
        <Image
          src="/relaydefaultappcicon.png"
          alt="Relay"
          width={72}
          height={72}
          priority
          style={{ display: 'block' }}
        />
      </div>
      <span style={{
        fontSize: 20,
        fontWeight: 600,
        color: '#1c1c1e',
        letterSpacing: -0.4,
        marginTop: 4,
      }}>
        Leaderboard
      </span>
      <span style={{
        fontSize: 14,
        color: '#8e8e93',
        letterSpacing: -0.2,
      }}>
        Top supporters of Relay
      </span>
    </div>
  );
}
