'use client';

import { useEffect, useRef } from 'react';
import './PaymentSuccess.css';

interface PaymentSuccessProps {
  amount: number;
  starsAmount: number;
  userPhotoUrl?: string;
  userInitials: string;
  onGoHome: () => void;
  onViewTransaction: () => void;
  topPadding?: number;
  bottomPadding?: number;
  leaderboardPosition?: number;
}

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  color: string;
  size: number;
  rotation: number;
  rotationSpeed: number;
  opacity: number;
  shape: 'rect' | 'circle' | 'star' | 'heart' | 'diamond' | 'sparkle';
  wave: number;
  shimmer: number;
  shimmerSpeed: number;
  trail: { x: number; y: number }[];
}

export function PaymentSuccess({
  amount,
  starsAmount,
  userPhotoUrl,
  userInitials,
  onGoHome,
  onViewTransaction,
  topPadding = 60,
  bottomPadding = 20,
  leaderboardPosition = 42,
}: PaymentSuccessProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Rich gold and celebration colors for maximum dopamine
    const colors = [
      '#FFD700', '#FFC107', '#FFEB3B', '#FFE082', // Golds
      '#FF6B6B', '#FF4757', '#FF69B4', '#E91E63', // Pinks/Reds
      '#4ECDC4', '#00CED1', '#00BCD4', '#26C6DA', // Teals
      '#2ED573', '#1E8E3E', '#4CAF50', '#8BC34A', // Greens (success!)
      '#1E90FF', '#2196F3', '#64B5F6', '#42A5F5', // Blues
      '#FFA502', '#FF9800', '#FFB74D', '#FFCC80', // Oranges
      '#E040FB', '#9C27B0', '#BA68C8', '#CE93D8', // Purples
      '#FFFFFF', '#F5F5F5', // Whites for sparkle
    ];
    
    const particles: Particle[] = [];
    const shapes: Array<'rect' | 'circle' | 'star' | 'heart' | 'diamond' | 'sparkle'> = 
      ['rect', 'circle', 'star', 'heart', 'diamond', 'sparkle'];

    // Create explosive burst with trails
    const createBurst = (centerX: number, centerY: number, count: number, wave: number, intensity: number = 1) => {
      for (let i = 0; i < count; i++) {
        const angle = (Math.PI * 2 * i) / count + Math.random() * 0.5;
        const speed = (Math.random() * 20 + 15) * intensity;
        
        particles.push({
          x: centerX,
          y: centerY,
          vx: Math.cos(angle) * speed * (0.8 + Math.random() * 0.4),
          vy: Math.sin(angle) * speed * (0.8 + Math.random() * 0.4) - 10,
          color: colors[Math.floor(Math.random() * colors.length)],
          size: Math.random() * 14 + 8,
          rotation: Math.random() * 360,
          rotationSpeed: (Math.random() - 0.5) * 30,
          opacity: 1,
          shape: shapes[Math.floor(Math.random() * shapes.length)],
          wave,
          shimmer: Math.random() * Math.PI * 2,
          shimmerSpeed: Math.random() * 0.3 + 0.1,
          trail: [],
        });
      }
    };

    // Create golden rain from top
    const createGoldenRain = () => {
      const goldColors = ['#FFD700', '#FFC107', '#FFEB3B', '#FFE082', '#FFFFFF'];
      for (let i = 0; i < 60; i++) {
        setTimeout(() => {
          particles.push({
            x: Math.random() * canvas.width,
            y: -20,
            vx: (Math.random() - 0.5) * 3,
            vy: Math.random() * 4 + 3,
            color: goldColors[Math.floor(Math.random() * goldColors.length)],
            size: Math.random() * 8 + 4,
            rotation: Math.random() * 360,
            rotationSpeed: (Math.random() - 0.5) * 15,
            opacity: 1,
            shape: Math.random() > 0.5 ? 'sparkle' : 'star',
            wave: 3,
            shimmer: Math.random() * Math.PI * 2,
            shimmerSpeed: Math.random() * 0.4 + 0.2,
            trail: [],
          });
        }, i * 30);
      }
    };

    // Create side fountains
    const createFountain = (x: number, direction: number) => {
      for (let i = 0; i < 25; i++) {
        setTimeout(() => {
          const angle = -Math.PI / 2 + (Math.random() - 0.5) * 0.8;
          const speed = Math.random() * 15 + 10;
          particles.push({
            x,
            y: canvas.height,
            vx: Math.cos(angle) * speed * direction + (Math.random() - 0.5) * 5,
            vy: Math.sin(angle) * speed - 5,
            color: colors[Math.floor(Math.random() * colors.length)],
            size: Math.random() * 10 + 6,
            rotation: Math.random() * 360,
            rotationSpeed: (Math.random() - 0.5) * 20,
            opacity: 1,
            shape: shapes[Math.floor(Math.random() * shapes.length)],
            wave: 4,
            shimmer: Math.random() * Math.PI * 2,
            shimmerSpeed: Math.random() * 0.3 + 0.1,
            trail: [],
          });
        }, i * 40);
      }
    };

    const centerX = canvas.width / 2;
    const centerY = canvas.height * 0.35;
    
    // Main explosion - bigger and more intense
    createBurst(centerX, centerY, 120, 0, 1.2);

    // Secondary bursts with staggered timing for cascading effect
    setTimeout(() => createBurst(canvas.width * 0.15, canvas.height * 0.25, 50, 1), 80);
    setTimeout(() => createBurst(canvas.width * 0.85, canvas.height * 0.25, 50, 1), 120);
    setTimeout(() => createBurst(canvas.width * 0.25, canvas.height * 0.12, 40, 2), 180);
    setTimeout(() => createBurst(canvas.width * 0.75, canvas.height * 0.12, 40, 2), 220);
    setTimeout(() => createBurst(centerX, centerY * 0.6, 60, 2, 0.8), 280);
    
    // Golden rain starts after initial burst
    setTimeout(createGoldenRain, 400);
    
    // Side fountains for extra celebration
    setTimeout(() => createFountain(canvas.width * 0.1, 1), 600);
    setTimeout(() => createFountain(canvas.width * 0.9, -1), 700);
    
    // Final celebratory burst
    setTimeout(() => createBurst(centerX, centerY, 80, 5, 1.5), 1200);

    let animationId: number;
    const startTime = Date.now();

    const drawStar = (ctx: CanvasRenderingContext2D, size: number) => {
      const spikes = 5;
      const outerRadius = size / 2;
      const innerRadius = size / 4;
      
      ctx.beginPath();
      for (let i = 0; i < spikes * 2; i++) {
        const radius = i % 2 === 0 ? outerRadius : innerRadius;
        const angle = (Math.PI * i) / spikes - Math.PI / 2;
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.fill();
    };

    const drawHeart = (ctx: CanvasRenderingContext2D, size: number) => {
      const s = size / 2;
      ctx.beginPath();
      ctx.moveTo(0, s * 0.3);
      ctx.bezierCurveTo(-s, -s * 0.3, -s, s * 0.6, 0, s);
      ctx.bezierCurveTo(s, s * 0.6, s, -s * 0.3, 0, s * 0.3);
      ctx.closePath();
      ctx.fill();
    };

    const drawDiamond = (ctx: CanvasRenderingContext2D, size: number) => {
      const s = size / 2;
      ctx.beginPath();
      ctx.moveTo(0, -s);
      ctx.lineTo(s * 0.6, 0);
      ctx.lineTo(0, s);
      ctx.lineTo(-s * 0.6, 0);
      ctx.closePath();
      ctx.fill();
    };

    const drawSparkle = (ctx: CanvasRenderingContext2D, size: number, shimmer: number) => {
      const s = size / 2;
      const pulse = 0.7 + Math.sin(shimmer) * 0.3;
      
      ctx.beginPath();
      // 4-pointed star sparkle
      ctx.moveTo(0, -s * pulse);
      ctx.lineTo(s * 0.15, -s * 0.15);
      ctx.lineTo(s * pulse, 0);
      ctx.lineTo(s * 0.15, s * 0.15);
      ctx.lineTo(0, s * pulse);
      ctx.lineTo(-s * 0.15, s * 0.15);
      ctx.lineTo(-s * pulse, 0);
      ctx.lineTo(-s * 0.15, -s * 0.15);
      ctx.closePath();
      ctx.fill();
    };

    const animate = () => {
      const elapsed = Date.now() - startTime;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach((p) => {
        // Store trail position
        if (p.trail.length < 5) {
          p.trail.push({ x: p.x, y: p.y });
        } else {
          p.trail.shift();
          p.trail.push({ x: p.x, y: p.y });
        }

        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.35; // Slightly less gravity for floatier feel
        p.vx *= 0.985;
        p.rotation += p.rotationSpeed;
        p.shimmer += p.shimmerSpeed;

        const fadeStart = 1500 + p.wave * 250;
        if (elapsed > fadeStart) {
          p.opacity = Math.max(0, p.opacity - 0.018);
        }

        if (p.opacity <= 0) return;

        // Draw trail for sparkles and stars
        if ((p.shape === 'sparkle' || p.shape === 'star') && p.trail.length > 1) {
          ctx.save();
          ctx.globalAlpha = p.opacity * 0.3;
          ctx.strokeStyle = p.color;
          ctx.lineWidth = p.size * 0.2;
          ctx.lineCap = 'round';
          ctx.beginPath();
          ctx.moveTo(p.trail[0].x, p.trail[0].y);
          for (let i = 1; i < p.trail.length; i++) {
            ctx.lineTo(p.trail[i].x, p.trail[i].y);
          }
          ctx.stroke();
          ctx.restore();
        }

        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate((p.rotation * Math.PI) / 180);
        
        // Add shimmer effect to opacity
        const shimmerOpacity = p.opacity * (0.85 + Math.sin(p.shimmer) * 0.15);
        ctx.globalAlpha = shimmerOpacity;
        ctx.fillStyle = p.color;

        switch (p.shape) {
          case 'rect':
            ctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2);
            break;
          case 'circle':
            ctx.beginPath();
            ctx.arc(0, 0, p.size / 3, 0, Math.PI * 2);
            ctx.fill();
            break;
          case 'star':
            drawStar(ctx, p.size);
            break;
          case 'heart':
            drawHeart(ctx, p.size);
            break;
          case 'diamond':
            drawDiamond(ctx, p.size);
            break;
          case 'sparkle':
            drawSparkle(ctx, p.size, p.shimmer);
            break;
        }

        ctx.restore();
      });

      // Extended animation duration for full celebration
      if (elapsed < 5500) {
        animationId = requestAnimationFrame(animate);
      }
    };

    animate();

    return () => {
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <div 
      className="payment-success" 
      style={{ 
        paddingTop: topPadding, 
        paddingBottom: bottomPadding,
      }}
    >
      {/* Confetti canvas - behind everything */}
      <canvas 
        ref={canvasRef} 
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
          zIndex: 0,
        }}
      />

      {/* Main content */}
      <div 
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
          zIndex: 1,
          paddingBottom: 24,
        }}
      >
        {/* Avatars with checkmark */}
        <div style={{ position: 'relative' }} className="success-avatar-container">
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div className="success-avatar" style={{ width: 64, height: 64 }}>
              {userPhotoUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={userPhotoUrl} alt="" className="success-avatar-image" />
              ) : (
                <span>{userInitials}</span>
              )}
            </div>
            <div className="success-avatar" style={{ width: 64, height: 64, background: '#4a90d9', marginLeft: -16 }}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src="/relaydefaultappcicon.png" alt="" className="success-avatar-image" />
            </div>
          </div>
          {/* Checkmark badge */}
          <div className="success-checkmark" style={{
            position: 'absolute',
            bottom: -4,
            right: -4,
            width: 32,
            height: 32,
            borderRadius: 16,
            background: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 8px rgba(0,0,0,0.16)',
          }}>
            <svg width={16} height={16} viewBox="0 0 24 24" fill="none">
              <path
                d="M5 13l4 4L19 7"
                stroke="#1e8e3e"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        </div>

        {/* Label */}
        <p style={{ 
          fontSize: 16, 
          fontWeight: 500, 
          color: 'rgba(255,255,255,0.88)', 
          margin: '24px 0 8px 0',
          letterSpacing: -0.2,
        }}>
          Sent to Relay
        </p>

        {/* Amount */}
        <h1 className="success-amount" style={{ 
          fontSize: 48, 
          fontWeight: 600, 
          color: '#fff', 
          margin: 0, 
          letterSpacing: -1.5,
          lineHeight: 1,
        }}>
          <span style={{ fontSize: 32, fontWeight: 500, color: 'rgba(255,255,255,0.7)', marginRight: 4 }}>$</span>
          {Number.isInteger(amount) ? amount : amount.toFixed(2)}
        </h1>

        {/* Stars badge */}
        <div className="success-stars-badge" style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: 8, 
          background: 'rgba(255,255,255,0.12)', 
          padding: '8px 16px', 
          borderRadius: 100,
          marginTop: 16,
        }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/telegram-stars.svg" alt="" width={20} height={20} />
          <span style={{ fontSize: 16, fontWeight: 600, color: '#fff', letterSpacing: -0.2 }}>{starsAmount}</span>
        </div>

        {/* Leaderboard info */}
        <p style={{ 
          fontSize: 16, 
          fontWeight: 500, 
          color: 'rgba(255,255,255,0.8)',
          marginTop: 32,
          textAlign: 'center',
          letterSpacing: -0.2,
        }}>
          You&apos;re <span className="success-leaderboard-position" style={{ 
            fontWeight: 600, 
            color: '#fff', 
            padding: '4px 8px', 
            borderRadius: 8,
            marginLeft: 4,
          }}>#{leaderboardPosition}</span> on the leaderboard
        </p>
      </div>

      {/* Buttons */}
      <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
        <button className="success-button-primary" onClick={onGoHome}>
          Done
        </button>
        <button className="success-button-secondary" onClick={onViewTransaction}>
          View Leaderboard
        </button>
      </div>
    </div>
  );
}
