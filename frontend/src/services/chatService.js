import { smartFetch } from './config';

export async function sendChatMessage({ message, language = 'en', context = {} }) {
  const res = await smartFetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      language,
      context,
    }),
  });
  if (!res.ok) {
    throw new Error(`Chat service error: ${res.status}`);
  }
  return res.json();
}
