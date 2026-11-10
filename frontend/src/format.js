// Prikaz števil in datumov v slovenski obliki: 1.200, 3,5, 10. 11. 2026

export function formatNumber(value) {
  return Number(value).toLocaleString("sl-SI", { maximumFractionDigits: 2 });
}

export function formatDate(value) {
  return new Date(value).toLocaleDateString("sl-SI");
}

export function formatDateTime(value) {
  return value ? new Date(value).toLocaleString("sl-SI", { dateStyle: "short", timeStyle: "short" }) : "–";
}

// Današnji datum v obliki 2026-11-10, ki jo uporabljata API in polje za datum
export function todayIso() {
  return new Date().toLocaleDateString("sv-SE");
}
