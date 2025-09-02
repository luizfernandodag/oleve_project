import { useState } from "react";
import { validatePins } from "./api";

type Pin = {
  image_url: string;
  title: string;
  pin_url: string;
  description: string;
  match_score: number;
  status: "approved" | "disqualified";
  ai_explanation: string;
};

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [pins, setPins] = useState<Pin[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<"all" | "approved" | "disqualified">("all");

  const handleStart = () => {
    if (!prompt) return;
    setLoading(true);
    setPins([]);

    // Chamada "síncrona" usando then/catch
    validatePins(prompt)
      .then(data => {
        if (data.status === "success") {
          setPins(data.pins);
        } else {
          alert("Erro ao validar pins: " + (data.message || "desconhecido"));
        }
      })
      .catch(err => {
        console.error("Erro ao validar pins:", err);
        alert("Erro ao validar pins. Veja o console.");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const filteredPins = pins.filter(pin => filter === "all" || pin.status === filter);

  return (
    <div className="p-4 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Oleve Prompts</h1>

      <div className="flex gap-2 mb-4">
        <input
          type="text"
          placeholder="Digite seu prompt visual"
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          className="border p-2 flex-1 rounded"
        />
        <button
          onClick={handleStart}
          className="bg-blue-600 text-white px-4 rounded hover:bg-blue-700"
          disabled={loading}
        >
          {loading ? "Processando..." : "Iniciar Prompt"}
        </button>
      </div>

      {pins.length > 0 && (
        <>
          <div className="mb-4 flex gap-2">
            <button
              className={`px-3 py-1 rounded border ${filter === "all" ? "bg-blue-200" : ""}`}
              onClick={() => setFilter("all")}
            >
              All
            </button>
            <button
              className={`px-3 py-1 rounded border ${filter === "approved" ? "bg-green-200" : ""}`}
              onClick={() => setFilter("approved")}
            >
              Approved
            </button>
            <button
              className={`px-3 py-1 rounded border ${filter === "disqualified" ? "bg-red-200" : ""}`}
              onClick={() => setFilter("disqualified")}
            >
              Disqualified
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {filteredPins.map((pin, idx) => (
              <div key={idx} className="border rounded p-2 shadow">
                <a href={pin.pin_url} target="_blank" rel="noopener noreferrer">
                  <img src={pin.image_url} alt={pin.title} className="w-full h-48 object-cover rounded mb-2" />
                </a>
                <h2 className="font-semibold">{pin.title}</h2>
                <p className="text-sm text-gray-600 mb-1">{pin.description}</p>
                <p className="text-sm">
                  Score: {pin.match_score.toFixed(2)} - {pin.status === "approved" ? "✅" : "❌"}
                </p>
                {pin.ai_explanation && <p className="text-xs text-gray-500 mt-1">{pin.ai_explanation}</p>}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
