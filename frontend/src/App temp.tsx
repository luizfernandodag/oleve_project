import { useState } from "react";
import { fetchPins, fetchSessions, startPrompt } from "./api";

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [pins, setPins] = useState<any[]>([]);
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleStart = async () => {
    setLoading(true);
    setPins([]);
    setSessions([]);

    try {
      const { prompt_id } = await startPrompt(prompt);

      // Polling sessions em paralelo
      const sessionData = await fetchSessions(prompt_id);
      setSessions(sessionData);

      // Polling pins
      const pinsData = await fetchPins(prompt_id);
      setPins(pinsData);
    } catch (err) {
      console.error("Error starting prompt:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Pinterest GPT Scraper</h1>
      <input
        type="text"
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
        className="border p-2 w-full mb-4"
        placeholder="Digite seu prompt"
      />
      <button
        onClick={handleStart}
        className="bg-blue-500 text-white px-4 py-2 rounded mb-4"
        disabled={loading}
      >
        {loading ? "Processando..." : "Iniciar Prompt"}
      </button>

      <div className="mb-4">
        <h2 className="font-semibold">Sessions:</h2>
        {sessions.map(s => (
          <div key={s._id} className="mb-1">
            <strong>{s.stage}</strong>: {s.status} - {s.log.join(", ")}
          </div>
        ))}
      </div>

      <div>
        <h2 className="font-semibold">Pins:</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {pins.map(pin => (
            <div key={pin._id} className="border p-2 rounded">
              <img src={pin.image_url} alt={pin.title} className="w-full h-32 object-cover mb-2"/>
              <h3 className="font-medium">{pin.title}</h3>
              <p className="text-sm">{pin.description}</p>
              <p className="text-sm">Score: {pin.match_score}</p>
              <p className="text-xs text-gray-500">{pin.ai_explanation}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
