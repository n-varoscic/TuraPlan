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

// Čas vožnje iz minut: 45 min, 2 h 5 min
export function formatDuration(minutes) {
  const hours = Math.floor(minutes / 60);
  return hours > 0 ? `${hours} h ${minutes % 60} min` : `${minutes} min`;
}

// Datum v obliki 2026-11-10, zamaknjen za dano število dni; računamo v UTC, da ga ne premakne prehod na poletni čas
export function addDays(date, days) {
  const result = new Date(date);
  result.setUTCDate(result.getUTCDate() + days);
  return result.toISOString().slice(0, 10);
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

// Število z ustreznim sklonom: pluralize(2, ["naročilo", "naročili", "naročila", "naročil"]) vrne »2 naročili«
export function pluralize(count, [one, two, few, many]) {
  const mod = count % 100;
  const word = mod === 1 ? one : mod === 2 ? two : mod === 3 || mod === 4 ? few : many;
  return `${count} ${word}`;
}
