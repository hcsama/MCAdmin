import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

async function handle({ request, params, fetch }: any) {
  const apiUrl = env.API_URL || 'http://localhost:8000';
  const path = params.path;

  // Construct the target URL
  const targetUrl = `${apiUrl}/${path}`;

  // Forward the request
  return await fetch(targetUrl, {
    method: request.method,
    headers: request.headers,
    body: request.method !== 'GET' && request.method !== 'HEAD' ? await request.blob() : undefined,
    redirect: 'manual'
  });
}

export const GET: RequestHandler = handle;
export const POST: RequestHandler = handle;
export const DELETE: RequestHandler = handle;
