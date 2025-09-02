const BASE_URL = "http://127.0.0.1:8080";

// Ative/desative mocks aqui
const USE_MOCK = false; // coloque true para testes com mock

export function validatePins(prompt: string) {
  return fetch(`${BASE_URL}/prompts/scrape-validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  })
    .then(res => {
      if (!res.ok) {
        return res.text().then(text => {
          console.error("Backend error:", text);
          throw new Error(`Error validating pins: ${res.status} ${res.statusText}`);
        });
      }
      return res.json();
    })
    .catch(err => {
      console.error("Network/backend error:", err);
      return { status: "error", pins: [] };
    });
}

export function startPrompt(text: string) {
  const endpoint = USE_MOCK ? "prompts/start/mock" : "scra";

  return fetch(`${BASE_URL}/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  })
    .then(res => {
      if (!res.ok) {
        return res.text().then(text => {
          console.error(`Backend error on /${endpoint}:`, text);
          throw new Error(`Error in prompt initialization: ${res.status} ${res.statusText}`);
        });
      }
      return res.json();
    })
    .catch(err => {
      console.error("Network/backend error:", err);
      return { status: "error", data: null };
    });
}
