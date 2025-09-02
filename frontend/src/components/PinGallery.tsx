// src/components/PinGallery.tsx
import { useState } from "react";
import { Pin } from "../types";

type Props = { pins: Pin[] };

export default function PinGallery({ pins }: Props) {
  const [threshold, setThreshold] = useState(0.5);

  const filteredPins = pins.filter(pin => pin.match_score >= threshold);

  return (
    <div>
      <label className="block mb-2">
        Minimum match score: {threshold.toFixed(2)}
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={threshold}
          onChange={(e) => setThreshold(parseFloat(e.target.value))}
          className="w-full"
        />
      </label>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {filteredPins.map((pin) => (
          <div key={pin.pin_url} className="border p-2 rounded shadow">
            <img src={pin.image_url} alt={pin.title} className="w-full h-48 object-cover" />
            <p className="font-bold">{pin.title}</p>
            <p>Score: {pin.match_score.toFixed(2)}</p>
            <p>{pin.status === "approved" ? "✅ Approved" : "❌ Disqualified"}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
