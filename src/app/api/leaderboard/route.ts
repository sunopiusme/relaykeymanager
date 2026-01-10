import { NextRequest, NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

// Configuration - should match bot's config
const DONATION_GOAL_STARS = 50000;
const STARS_PER_DOLLAR = 50;

interface Donor {
  id: number;
  name: string;
  username: string | null;
  total_stars: number;
  total_usd: number;
  donation_count: number;
  first_donation: string;
  last_donation: string;
  photo_url?: string;
}

interface DonationsData {
  donors: Record<string, Donor>;
  total_stars: number;
  total_usd: number;
  transactions: unknown[];
  last_milestone?: number;
}

async function loadDonationsData(): Promise<DonationsData | null> {
  try {
    // Try to read from bot's data directory
    const donationsPath = path.join(process.cwd(), 'telegram-bot', 'data', 'donations.json');
    const data = await fs.readFile(donationsPath, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    console.log('Could not read donations file:', error);
    return null;
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');
    
    const data = await loadDonationsData();
    
    // If no data file exists yet, return empty state
    if (!data) {
      return NextResponse.json({
        leaderboard: [],
        stats: {
          total_stars: 0,
          total_usd: 0,
          total_donors: 0,
          goal_stars: DONATION_GOAL_STARS,
          goal_usd: DONATION_GOAL_STARS / STARS_PER_DOLLAR,
        },
        currentUser: null,
      });
    }
    
    // Convert donors object to array and sort by total_stars
    const donorsArray = Object.values(data.donors);
    const sortedDonors = donorsArray.sort((a, b) => b.total_stars - a.total_stars);
    
    // Map to leaderboard format with ranks
    const leaderboard = sortedDonors.slice(0, 100).map((donor, index) => ({
      id: donor.id,
      name: donor.name,
      username: donor.username || '',
      amount: donor.total_usd,
      rank: index + 1,
      photoUrl: donor.photo_url,
    }));

    // Find current user if userId provided
    let currentUser = null;
    if (userId) {
      const userIdNum = parseInt(userId);
      const userIndex = sortedDonors.findIndex(d => d.id === userIdNum);
      
      if (userIndex !== -1) {
        const donor = sortedDonors[userIndex];
        currentUser = {
          id: donor.id,
          name: donor.name,
          username: donor.username || '',
          amount: donor.total_usd,
          rank: userIndex + 1,
          photoUrl: donor.photo_url,
        };
      }
    }

    return NextResponse.json({
      leaderboard,
      stats: {
        total_stars: data.total_stars,
        total_usd: data.total_usd,
        total_donors: donorsArray.length,
        goal_stars: DONATION_GOAL_STARS,
        goal_usd: DONATION_GOAL_STARS / STARS_PER_DOLLAR,
      },
      currentUser,
    });
  } catch (error) {
    console.error('Leaderboard error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch leaderboard' },
      { status: 500 }
    );
  }
}
