// Prikaz števil in datumov v slovenski obliki: 1.200, 3,5, 10. 11. 2026

export function formatNumber(value) {
  return Number(value).toLocaleString("sl-SI", { maximumFractionDigits: 2, useGrouping: "always" });
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

// Število palet s pravilnim sklonom za »Preseženo za …«: 1 paleto, 2 paleti, 3 palete, 5 palet, 1,5 palete
export function formatPallets(value) {
  const number = Number(value);
  const mod = number % 100;
  let word = "palet";
  if (!Number.isInteger(number) || mod === 3 || mod === 4) word = "palete";
  else if (mod === 1) word = "paleto";
  else if (mod === 2) word = "paleti";
  return `${formatNumber(number)} ${word}`;
}
