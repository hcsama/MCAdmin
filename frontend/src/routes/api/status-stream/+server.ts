import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ fetch }) => {
  const apiUrl = env.API_URL || 'http://localhost:8000';
  let isAborted = false;

  const stream = new ReadableStream({
    async start(controller) {
      let retryDelay = 1000;

      while (!isAborted) {
        try {
          const response = await fetch(`${apiUrl}/status-stream`, {
            headers: { 'Accept': 'text/event-stream' },
            cache: 'no-store'
          });

          if (!response.ok) throw new Error(`API returned ${response.status}`);

          // Reset retry delay on successful connection
          retryDelay = 1000;

          const reader = response.body?.getReader();
          if (!reader) throw new Error('No reader available');

          try {
            while (!isAborted) {
              const { done, value } = await reader.read();
              if (done) break;
              controller.enqueue(value);
            }
          } finally {
            reader.releaseLock();
          }
        } catch (error: any) {
          if (isAborted) break;
          console.error('BFF SSE connection to API lost, retrying in', retryDelay, 'ms:', error.message);

          await new Promise(resolve => setTimeout(resolve, retryDelay));
          // Exponential backoff
          retryDelay = Math.min(retryDelay * 2, 30000);
        }
      }

      try {
        controller.close();
      } catch (e) {
        // Stream might already be closed
      }
    },
    cancel() {
      isAborted = true;
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    }
  });
};
