'use client';

interface DonationButtonProps {
  onProceed: () => void;
  isLoading?: boolean;
  loadingText?: string;
}

export function DonationButton({ 
  onProceed, 
  isLoading = false,
  loadingText = 'Processing...'
}: DonationButtonProps) {
  return (
    <button
      onClick={onProceed}
      disabled={isLoading}
      style={{
        width: '100%',
        height: 56,
        borderRadius: 28,
        border: 'none',
        background: isLoading ? '#5a9fff' : '#007AFF',
        color: '#fff',
        fontSize: 17,
        fontWeight: 600,
        cursor: isLoading ? 'not-allowed' : 'pointer',
        WebkitTapHighlightColor: 'transparent',
        transition: 'transform 0.12s ease, opacity 0.12s ease, background 0.2s ease',
        letterSpacing: -0.2,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 8,
        opacity: isLoading ? 0.85 : 1,
      }}
      onMouseDown={(e) => {
        if (!isLoading) {
          e.currentTarget.style.transform = 'scale(0.98)';
          e.currentTarget.style.opacity = '0.92';
        }
      }}
      onMouseUp={(e) => {
        e.currentTarget.style.transform = 'scale(1)';
        e.currentTarget.style.opacity = isLoading ? '0.85' : '1';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'scale(1)';
        e.currentTarget.style.opacity = isLoading ? '0.85' : '1';
      }}
    >
      {isLoading && (
        <svg 
          width="20" 
          height="20" 
          viewBox="0 0 24 24" 
          style={{ 
            animation: 'spin 1s linear infinite',
          }}
        >
          <style>{`
            @keyframes spin {
              from { transform: rotate(0deg); }
              to { transform: rotate(360deg); }
            }
          `}</style>
          <circle
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="3"
            fill="none"
            strokeLinecap="round"
            strokeDasharray="31.4 31.4"
            strokeDashoffset="10"
          />
        </svg>
      )}
      {isLoading ? loadingText : 'Pay'}
    </button>
  );
}
