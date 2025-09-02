import { useState } from "react";

interface Pin {
  image_url: string;
  title: string;
  pin_url: string;
  description: string;
}

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [pins, setPins] = useState<Pin[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleScrape = async () => {
    if (!prompt) return;
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/prompts/scrape-direct", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!res.ok) {
        throw new Error(`Erro na API: ${res.status}`);
      }

      const data = await res.json();

      // Garante que data.pins existe
      setPins(data.pins || []);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Erro inesperado");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center p-6">
      <h1 className="text-2xl font-bold mb-4">Pinterest Scraper</h1>

      <div className="flex gap-2 mb-6">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Digite um prompt"
          className="px-4 py-2 border rounded-lg w-80"
        />
        <button
          onClick={handleScrape}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:opacity-50"
        >
          {loading ? "Buscando..." : "Buscar"}
        </button>
      </div>

      {error && <p className="text-red-500 mb-4">{error}</p>}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-5xl">
        {pins.map((pin, idx) => (
          <div key={idx} className="bg-white shadow rounded-lg p-4">
            <img
              src={pin.image_url}
              alt={pin.title}
              className="w-full h-48 object-cover rounded-md mb-2"
            />
            <h2 className="font-semibold">{pin.title}</h2>
            <p className="text-sm text-gray-600">{pin.description}</p>
            <a
              href={pin.pin_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 text-sm"
            >
              Ver no Pinterest
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
