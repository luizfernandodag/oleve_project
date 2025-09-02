const BASE_URL = "http://127.0.0.1:8080";

// Ative/desative mocks aqui
const USE_MOCK = false; // coloque true para testes com mock

export async function fetchData(endpoint: string) {
  const res = await fetch(`http://localhost:8080/${endpoint}`, {
    method: "GET", // se for POST
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: "exemplo" })
  });
  if (!res.ok) throw new Error('Erro na API');
  return res.json();
}

// async function fetchData(endpoint: string) {
//   try {
//     const res = await fetch(`${BASE_URL}/${endpoint}`);
//     const res = await fetch(`${BASE_URL}/${endpoint}`);
//     if (!res.ok) {
//       const errorText = await res.text();
//       console.error(`Error fetching ${endpoint}:`, errorText);
//       throw new Error(`Error in API: ${res.status} ${res.statusText}`);
//     }
//     return res.json();
//   } catch (err) {
//     console.error(`Network error fetching ${endpoint}:`, err);
//     throw err;
//   }
// }

// ------------------------------
// Start prompt
// ------------------------------
export async function startPrompt(text: string) {
  const endpoint = USE_MOCK ? "prompts/start/mock" : "scraper/run";

  const res = await fetch(`${BASE_URL}/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  if (!res.ok) {
    const errorText = await res.text();
    console.error(`Backend error on /${endpoint}:`, errorText);
    throw new Error(`Error in prompt initialization: ${res.status} ${res.statusText}`);
  }

  const data = await res.json();
  return data;
}

// ------------------------------
// Polling sessions
// ------------------------------
export async function fetchSessions(prompt_id: string, retries = 20, delayMs = 1000) {
  for (let i = 0; i < retries; i++) {
    try {
      const sessions = await fetchData(`sessions/${prompt_id}`);
      if (sessions.every((s: any) => s.status === "completed")) {
        return sessions;
      }
    } catch (err) {
      // ignora erro e tenta novamente
    }
    await new Promise(res => setTimeout(res, delayMs));
  }
  throw new Error(`Sessions not completed after ${retries} retries`);
}

// ------------------------------
// Polling pins
// ------------------------------
export async function fetchPins(prompt_id: string, retries = 20, delayMs = 1000) {
  for (let i = 0; i < retries; i++) {
    try {
      const pins = await fetchData(`pins/${prompt_id}`);
      if (pins.length > 0) return pins;
    } catch (err) {
      // ignora erro e tenta novamente
    }
    await new Promise(res => setTimeout(res, delayMs));
  }
  throw new Error(`Pins not available after ${retries} retries`);
}


export async function startScraper() {
  const res = await fetch("http://127.0.0.1:8080/start-scraper", {
    method: "POST",
  });
  return res.json();
}