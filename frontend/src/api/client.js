// Vsi klici na backend gredo skozi to datoteko

// Naslov API-ja se lahko nastavi z VITE_API_URL (npr. v Dockerju)
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

// Pošlje GET zahtevo in vrne odgovor kot JSON, ob napaki vrže izjemo
async function apiGet(path) {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Napaka ${response.status} pri ${path}`);
  }
  return response.json();
}

export function getHealth() {
  return apiGet("/health/");
}
