// src/App.tsx
import { useEffect, useState } from "react";

type Pin = {
  pin_url: string;
  image_url: string;
  title: string;
  description: string;
  match_score: number;
  status: "approved" | "disqualified";
  ai_explanation: string;
};

type PromptHistoryEntry = {
  prompt: string;
  pins: Pin[];
};

const LOCAL_STORAGE_KEY = "prompt_history";

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [pins, setPins] = useState<Pin[]>([]);
  const [history, setHistory] = useState<PromptHistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [minScore, setMinScore] = useState(0.5);

  // Load history from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (stored) setHistory(JSON.parse(stored));
  }, []);

  // Save history to localStorage
  const saveHistory = (newEntry: PromptHistoryEntry) => {
    const newHistory = [newEntry, ...history];
    setHistory(newHistory);
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(newHistory));
  };

  const handleSubmit = async () => {
    if (!prompt) return;
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8080/prompts/scrape-validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      if (!res.ok) throw new Error("API error");
      const data = await res.json();
      const validatedPins: Pin[] = data.pins || [];
      setPins(validatedPins);
      saveHistory({ prompt, pins: validatedPins });
    } catch (err: any) {
      console.error("Fetch error:", err);
      setPins([]);
    } finally {
      setLoading(false);
    }
  };

  // Filter pins by minimum score
  const filteredPins = pins.filter((pin) => pin.match_score >= minScore);

  return (
    <div className="p-4 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Pinterest AI Scraper</h1>

      <div className="mb-4 flex gap-2">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your visual prompt..."
          className="border p-2 flex-1"
        />
        <button
          onClick={handleSubmit}
          className="bg-blue-500 text-white px-4 py-2 rounded"
          disabled={loading}
        >
          {loading ? "Loading..." : "Start Agent"}
        </button>
      </div>

      <div className="mb-4">
        <label>Min Match Score: {minScore}</label>
        <input
          type="range"
          min={0}
          max={1}
          step={0.05}
          value={minScore}
          onChange={(e) => setMinScore(parseFloat(e.target.value))}
          className="w-full"
        />
      </div>

      {filteredPins.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-8">
          {filteredPins.map((pin) => (
            <div key={pin.pin_url} className="border p-2 rounded">
              <img
                src={pin.image_url}
                alt={pin.title}
                className="w-full h-48 object-cover mb-2"
              />
              <h3 className="font-semibold">{pin.title}</h3>
              <p className="text-sm mb-1">{pin.description}</p>
              <p>
                Score: {pin.match_score.toFixed(2)} - {pin.status === "approved" ? "✅" : "❌"}
              </p>
              <p className="text-xs italic">{pin.ai_explanation}</p>
            </div>
          ))}
        </div>
      )}

      {history.length > 0 && (
        <div className="mt-8">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-xl font-bold">Prompt History</h2>
            <button
              onClick={() => {
                if (confirm("Are you sure you want to clear history?")) {
                  setHistory([]);
                  localStorage.removeItem(LOCAL_STORAGE_KEY);
                }
              }}
              className="bg-red-500 text-white px-3 py-1 rounded text-sm"
            >
              Clear History
            </button>
          </div>

          {history.map((entry, idx) => (
            <div key={idx} className="mb-4 border p-2 rounded">
              <h3 className="font-semibold">{entry.prompt}</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 mt-2">
                {entry.pins.map((pin) => (
                  <div key={pin.pin_url} className="border p-1 rounded text-xs">
                    <img
                      src={pin.image_url}
                      alt={pin.title}
                      className="w-full h-24 object-cover rounded mb-1"
                    />
                    <p>Score: {pin.match_score.toFixed(2)}</p>
                    <p>Status: {pin.status === "approved" ? "✅" : "❌"}</p>
                    <p className="italic">{pin.ai_explanation}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
