// Vsi klici na backend gredo skozi to datoteko

// Naslov API-ja se lahko nastavi z VITE_API_URL (npr. v Dockerju)
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

// Django Admin teče na istem strežniku kot API
export const ADMIN_URL = API_URL.replace(/\/api$/, "/admin/");

// Žetona hranimo v brskalniku, da prijava ostane tudi po osvežitvi strani
const ACCESS_KEY = "accessToken";
const REFRESH_KEY = "refreshToken";

export function hasToken() {
  return localStorage.getItem(ACCESS_KEY) !== null;
}

function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

// Z žetonom za osvežitev pridobi nov dostopni žeton, vrne true ob uspehu
async function refreshAccessToken() {
  const refresh = localStorage.getItem(REFRESH_KEY);
  if (!refresh) return false;
  const response = await fetch(`${API_URL}/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });
  if (!response.ok) return false;
  const data = await response.json();
  localStorage.setItem(ACCESS_KEY, data.access);
  return true;
}

// Besedilo napake iz odgovora: {"detail": "…"}, ["razlog", …] ali {"polje": ["razlog"]}
function errorMessage(data, status) {
  if (!data) return `Napaka ${status}`;
  if (data.detail) return data.detail;
  return Object.values(data).flat().join(" ");
}

// Pošlje zahtevo z žetonom v glavi in vrne odgovor kot JSON
async function apiRequest(path, { method = "GET", body } = {}, retry = true) {
  const headers = { "Content-Type": "application/json" };
  const token = localStorage.getItem(ACCESS_KEY);
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  // Dostopni žeton je potekel: enkrat ga osvežimo in zahtevo ponovimo
  if (response.status === 401 && token && retry) {
    if (await refreshAccessToken()) return apiRequest(path, { method, body }, false);
    clearTokens();
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(errorMessage(data, response.status));
    error.status = response.status;
    error.data = data;
    throw error;
  }
  return data;
}

export async function login(email, password) {
  const data = await apiRequest("/auth/login/", { method: "POST", body: { email, password } });
  localStorage.setItem(ACCESS_KEY, data.access);
  localStorage.setItem(REFRESH_KEY, data.refresh);
}

export function logout() {
  clearTokens();
}

export function getMe() {
  return apiRequest("/auth/me/");
}

// Seznam tur, filtri so neobvezni: { date_from: "2026-11-10", status: "DRAFT" }
export function getTours(filters = {}) {
  const params = new URLSearchParams(Object.entries(filters).filter(([, value]) => value));
  return apiRequest(`/tours/?${params}`);
}

export function getTour(id) {
  return apiRequest(`/tours/${id}/`);
}

// Zamenja vozilo osnutka in vrne posodobljeno turo
export function changeVehicle(tourId, vehicleId) {
  return apiRequest(`/tours/${tourId}/`, { method: "PATCH", body: { vehicle: vehicleId } });
}

// Prosta vozila in vozniki za novo turo na izbrani datum
export function getTourOptions(date) {
  return apiRequest(`/tours/options/?date=${date}`);
}

export function createTour(data) {
  return apiRequest("/tours/", { method: "POST", body: data });
}

// Nerazporejena naročila, ki jih lahko dodamo v turo z datumom odpreme date
export function getOrders(date) {
  return apiRequest(`/orders/?date=${date}`);
}

// Dodajanje in odstranjevanje postanka vrneta posodobljeno turo
export function addStop(tourId, orderId) {
  return apiRequest(`/tours/${tourId}/stops/`, { method: "POST", body: { order: orderId } });
}

export function removeStop(stopId) {
  return apiRequest(`/stops/${stopId}/`, { method: "DELETE" });
}

// Premik postanka za eno mesto, direction je "up" ali "down"
export function moveStop(stopId, direction) {
  return apiRequest(`/stops/${stopId}/move/`, { method: "POST", body: { direction } });
}

// Premik postanka na poljubno mesto, npr. ob vlečenju z miško
export function moveStopTo(stopId, position) {
  return apiRequest(`/stops/${stopId}/move/`, { method: "POST", body: { position } });
}

// Stalna opomba stranke postanka, prazna opomba jo odstrani
export function updateDeliveryNote(stopId, deliveryNote) {
  return apiRequest(`/stops/${stopId}/delivery-note/`, { method: "POST", body: { delivery_note: deliveryNote } });
}

export function updateDriverNote(stopId, driverNote) {
  return apiRequest(`/stops/${stopId}/`, { method: "PATCH", body: { driver_note: driverNote } });
}
