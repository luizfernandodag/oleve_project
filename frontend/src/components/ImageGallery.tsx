// frontend/src/components/ImageGallery.tsx
import React, { useEffect, useState } from "react";

type Pin = {
  image_url: string;
  title: string;
  pin_url: string;
  description: string;
  match_score: number;
  status: "approved" | "disqualified";
  ai_explanation: string;
};

type Filter = "all" | "approved" | "disqualified";

const ImageGallery: React.FC<{ prompt: string }> = ({ prompt }) => {
  const [pins, setPins] = useState<Pin[]>([]);
  const [filter, setFilter] = useState<Filter>("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPins = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/validate-pins?prompt=${encodeURIComponent(prompt)}`);
        const data = await res.json();
        if (data.status === "success") {
          setPins(data.pins);
        } else {
          setError(data.message || "Erro ao carregar pins");
        }
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPins();
  }, [prompt]);

  const filteredPins = pins.filter(pin => {
    if (filter === "all") return true;
    return pin.status === filter;
  });

  return (
    <div>
      <div className="flex gap-2 mb-4">
        <button onClick={() => setFilter("all")} className="px-3 py-1 bg-gray-200 rounded">All</button>
        <button onClick={() => setFilter("approved")} className="px-3 py-1 bg-green-200 rounded">Approved</button>
        <button onClick={() => setFilter("disqualified")} className="px-3 py-1 bg-red-200 rounded">Disqualified</button>
      </div>

      {loading && <p>Loading pins...</p>}
      {error && <p className="text-red-500">{error}</p>}

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {filteredPins.map((pin, idx) => (
          <div key={idx} className="border rounded shadow p-2">
            <a href={pin.pin_url} target="_blank" rel="noopener noreferrer">
              <img src={pin.image_url} alt={pin.title} className="w-full h-48 object-cover rounded" />
            </a>
            <h3 className="font-semibold mt-2">{pin.title}</h3>
            <p className="text-sm text-gray-600">{pin.description}</p>
            <div className="flex items-center mt-1">
              <div className="flex-1 h-2 bg-gray-300 rounded mr-2">
                <div
                  className={`h-2 rounded ${pin.status === "approved" ? "bg-green-500" : "bg-red-500"}`}
                  style={{ width: `${pin.match_score * 100}%` }}
                />
              </div>
              <span className="text-sm">{pin.match_score.toFixed(2)}</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">{pin.ai_explanation}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ImageGallery;
