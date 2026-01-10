'use client';

import Image from 'next/image';

export function DonationHeader() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 0,
      paddingTop: 8,
      paddingBottom: 16,
    }}>
      <div style={{
        width: 100,
        height: 100,
        borderRadius: 25,
        overflow: 'hidden',
        background: '#e5e5ea',
      }}>
        <Image
          src="/relaydefaultappcicon.png"
          alt="Relay"
          width={100}
          height={100}
          priority
          style={{ display: 'block' }}
        />
      </div>
      <span style={{
        fontSize: 16,
        fontWeight: 500,
        color: '#1c1c1e',
        letterSpacing: -0.3,
        marginTop: 4,
      }}>
        Relay
      </span>
    </div>
  );
}
