// import { useState } from "react";
// import { startPrompt } from "./api";

// function App() {
//   const [input, setInput] = useState("");
//   const [result, setResult] = useState<any>(null);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState<string | null>(null);

//   const handleStartPrompt = async () => {
//     setLoading(true);
//     setError(null);
//     setResult(null);

//     try {
//       const data = await startPrompt(input);
//       setResult(data);
//     } catch (err: any) {
//       setError(err.message || "Erro desconhecido");
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleTestHello = async () => {
//     setLoading(true);
//     setError(null);
//     setResult(null);

//     try {
//       const data = await fetchHello();
//       setResult(data);
//     } catch (err: any) {
//       setError(err.message || "Erro desconhecido");
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-6">
//       <div className="bg-white shadow-lg rounded-2xl p-6 w-full max-w-lg space-y-4">
//         <h1 className="text-2xl font-bold text-center text-gray-800">
//           Oleve Prompts
//         </h1>

//         <input
//           type="text"
//           placeholder="Digite seu prompt..."
//           value={input}
//           onChange={(e) => setInput(e.target.value)}
//           className="w-full p-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400"
//         />

//         <div className="flex gap-3">
//           <button
//             onClick={handleStartPrompt}
//             disabled={loading}
//             className="flex-1 bg-blue-500 text-white px-4 py-2 rounded-xl hover:bg-blue-600 disabled:opacity-50"
//           >
//             Iniciar Prompt
//           </button>

//           <button
//             onClick={handleTestHello}
//             disabled={loading}
//             className="flex-1 bg-green-500 text-white px-4 py-2 rounded-xl hover:bg-green-600 disabled:opacity-50"
//           >
//             Testar Hello
//           </button>
//         </div>

//         {loading && (
//           <p className="text-blue-500 text-center">Carregando...</p>
//         )}

//         {error && <p className="text-red-500 text-center">{error}</p>}

//         {result && (
//           <pre className="bg-gray-100 p-4 rounded-xl text-sm overflow-x-auto">
//             {JSON.stringify(result, null, 2)}
//           </pre>
//         )}
//       </div>
//     </div>
//   );
// }

// export default App;


// frontend/src/App.tsx
import { useState } from "react";
import { startPrompt } from "./api";

interface Pin {
  image_url: string;
  title: string;
  pin_url: string;
  description: string;
}

function App() {
  const [prompt, setPrompt] = useState("");
  const [pins, setPins] = useState<Pin[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStart = async () => {
    if (!prompt) return;
    setLoading(true);
    setError(null);
    setPins([]);

    try {
      const res = await startPrompt(prompt);
      if (res.status === "success" && res.pins) {
        setPins(res.pins);
      } else {
        setError(res.message || "Erro ao iniciar prompt");
      }
    } catch (err: any) {
      setError(err.message || "Erro desconhecido");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Oleve Prompts</h1>

      <input
        type="text"
        placeholder="Digite o prompt"
        className="border p-2 rounded w-full mb-4"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />

      <div className="flex gap-2 mb-4">
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
          onClick={handleStart}
          disabled={loading}
        >
          {loading ? "Carregando..." : "Iniciar Prompt"}
        </button>
      </div>

      {error && <p className="text-red-500 mb-4">{error}</p>}

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {pins.map((pin, index) => (
          <a
            key={index}
            href={pin.pin_url}
            target="_blank"
            rel="noopener noreferrer"
            className="border rounded overflow-hidden hover:shadow-lg transition-shadow"
          >
            <img
              src={pin.image_url}
              alt={pin.title}
              className="w-full h-48 object-cover"
            />
            <div className="p-2">
              <h2 className="font-semibold">{pin.title}</h2>
              <p className="text-sm text-gray-600">{pin.description}</p>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

export default App;
