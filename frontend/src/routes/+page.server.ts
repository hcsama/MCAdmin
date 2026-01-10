import { env } from '$env/dynamic/private';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
  const apiUrl = env.API_URL || 'http://localhost:8000';

  try {
    const response = await fetch(`${apiUrl}/status`);
    const data = await response.json();

    return {
      status: data
    };
  } catch (error) {
    console.error('Failed to fetch server status:', error);
    return {
      status: {
        server: { online: false, version: 'Unknown', motd: 'Offline', error: 'Could not connect to API server' },
        world: { time: 0, time_formatted: '06:00', phase: 'Day', days: 0, daylight_cycle: true, weather: 'clear', weather_cycle: true },
        players: { online: 0, max: 0, list: [] },
        whitelist: { enabled: false, members: [] },
        gamerules: { rules: {} }
      }
    };
  }
};
