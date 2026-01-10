'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTelegram } from '@/hooks/useTelegram';
import { DonationHeader } from './DonationHeader';
import { DonationCard } from './DonationCard';
import { UserDetails } from './UserDetails';
import { DonationButton } from './DonationButton';
import { PaymentSuccess } from './PaymentSuccess';
import './DonationPage.css';

const DONATION_AMOUNT_USD = 4.99;
const STARS_PER_DOLLAR = 50;

export function DonationPage() {
  const router = useRouter();
  const { user, hapticFeedback, contentSafeAreaInset, safeAreaInset, close, setHeaderColor, setBackgroundColor } = useTelegram();
  const [paymentState, setPaymentState] = useState<'idle' | 'processing' | 'success'>('idle');
  
  const starsAmount = DONATION_AMOUNT_USD * STARS_PER_DOLLAR;

  const handleProceed = async () => {
    hapticFeedback.impact('medium');
    
    // Start transition immediately
    setPaymentState('processing');
    
    // Small delay then show success with color change
    setTimeout(() => {
      setHeaderColor('#1e8e3e');
      setBackgroundColor('#1e8e3e');
      hapticFeedback.notification('success');
      setPaymentState('success');
      
      // Send data to bot after successful payment
      const tg = window.Telegram?.WebApp;
      if (tg?.sendData) {
        try {
          tg.sendData(JSON.stringify({
            action: 'donation_complete',
            amount: starsAmount,
            usd: DONATION_AMOUNT_USD,
            rank: 42, // TODO: Get actual rank from backend
            userId: user?.id,
          }));
        } catch (e) {
          console.log('Could not send data to bot:', e);
        }
      }
    }, 250);
  };

  const handleGoHome = () => {
    hapticFeedback.impact('light');
    // Reset colors before closing
    setHeaderColor('#f2f2f7');
    setBackgroundColor('#f2f2f7');
    close();
  };

  const handleViewLeaderboard = () => {
    hapticFeedback.impact('light');
    // Reset colors before navigating
    setHeaderColor('#f2f2f7');
    setBackgroundColor('#f2f2f7');
    router.push('/leaderboard');
  };

  // Get user initials
  const getUserInitials = () => {
    if (!user) return 'U';
    const firstName = user.first_name || '';
    const lastName = user.last_name || '';
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase() || 'U';
  };

  const topPadding = Math.max(contentSafeAreaInset.top, safeAreaInset.top, 8) + 80;
  const bottomPadding = Math.max(contentSafeAreaInset.bottom, safeAreaInset.bottom, 24);

  return (
    <div className="donation-page-container">
      {/* Success screen */}
      {paymentState === 'success' && (
        <div className="success-screen">
          <PaymentSuccess
            amount={DONATION_AMOUNT_USD}
            starsAmount={starsAmount}
            userPhotoUrl={user?.photo_url}
            userInitials={getUserInitials()}
            onGoHome={handleGoHome}
            onViewTransaction={handleViewLeaderboard}
            topPadding={topPadding}
            bottomPadding={bottomPadding}
          />
        </div>
      )}

      {/* Main donation page */}
      <div 
        className={`donation-page-main ${paymentState !== 'idle' ? 'fade-out' : ''}`}
        style={{
          paddingTop: topPadding,
          paddingBottom: bottomPadding,
        }}
      >
        {/* Content section */}
        <div className="donation-content">
          <DonationHeader />
          <DonationCard amount={DONATION_AMOUNT_USD} starsAmount={starsAmount} />
        </div>

        {/* Details section */}
        <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
          <UserDetails user={user} starsAmount={starsAmount} usdAmount={DONATION_AMOUNT_USD} />
          
          {/* Footer section */}
          <div>
            <DonationButton onProceed={handleProceed} />
          </div>
          <p style={{
            textAlign: 'center',
            fontSize: 12,
            color: '#8e8e93',
            margin: 0,
            letterSpacing: -0.1,
          }}>
            Secured by <span style={{ fontWeight: 600, color: '#636366' }}>Relay</span>
          </p>
        </div>
      </div>
    </div>
  );
}
