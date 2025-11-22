import axios from 'axios';

const BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export async function planRequest(message, intents) {
  const payload = intents && intents.length ? { message, intents } : { message };
  const resp = await axios.post(`${BASE_URL}/api/plan`, payload);
  return resp.data;
}
