const BASE_URL = "http://127.0.0.1:8000";
const USE_MOCK = false; // se true, usa endpoints de mock no backend

export async function fetchHello() {
  const res = await fetch(`${BASE_URL}/hello`);
  if (!res.ok) {
    throw new Error(`Erro no backend: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

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
    throw new Error(
      `Error in prompt initialization: ${res.status} ${res.statusText}`
    );
  }

  return res.json();
}
