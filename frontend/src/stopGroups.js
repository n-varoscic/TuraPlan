// Zaporedne postanke iste stranke združimo v skupino, ki je prikazana z enakim ozadjem
export function groupStops(stops) {
  const groups = [];
  for (const stop of stops) {
    const last = groups.at(-1);
    if (last && last.customerId === stop.customer_id) last.stops.push(stop);
    else groups.push({ customerId: stop.customer_id, customer: stop.customer, stops: [stop] });
  }
  return groups;
}
