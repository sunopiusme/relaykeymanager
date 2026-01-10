'use client';

interface DonationCardProps {
  amount: number;
  starsAmount: number;
}

export function DonationCard({ amount, starsAmount }: DonationCardProps) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 0,
      padding: '0 0 24px 0',
    }}>
      <h1 style={{
        fontSize: 48,
        fontWeight: 600,
        color: '#1c1c1e',
        margin: 0,
        letterSpacing: -1.5,
        lineHeight: 1,
        marginTop: 0,
      }}>
        <span style={{ fontSize: 32, fontWeight: 500, color: '#636366', marginRight: 4 }}>$</span>
        {Number.isInteger(amount) ? amount : amount.toFixed(2)}
      </h1>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        padding: '8px 16px',
        background: 'rgba(0,0,0,0.05)',
        borderRadius: 100,
        marginTop: 16,
      }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/telegram-stars.svg" alt="" width={20} height={20} />
        <span style={{
          fontSize: 16,
          fontWeight: 600,
          color: '#1c1c1e',
          letterSpacing: -0.2,
        }}>
          {starsAmount}
        </span>
      </div>
    </div>
  );
}
