import { useEffect } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { MapContainer, Marker, Polyline, Popup, TileLayer, useMap } from "react-leaflet";
import { formatDate, formatNumber } from "../format.js";
import { groupStops } from "../stopGroups.js";

// Okrogla oznaka z besedilom: številka postanka ali S za skladišče
function markerIcon(label, className = "") {
  return L.divIcon({
    html: `<span class="${className}">${label}</span>`,
    className: "tp-map-marker",
    iconSize: [0, 0],
    popupAnchor: [0, -14],
  });
}

// Pogled zemljevida se prilagodi tako, da so vidne vse točke ture
function FitPoints({ points, large }) {
  const map = useMap();
  // Besedilo se spremeni samo, ko se spremenijo točke, zato se pogled ne premika brez razloga
  const key = JSON.stringify(points);
  useEffect(() => {
    // Ob povečanju ali pomanjšanju mora Leaflet na novo izmeriti velikost zemljevida
    map.invalidateSize();
    const bounds = JSON.parse(key);
    if (bounds.length > 0) map.fitBounds(bounds, { padding: [30, 30], maxZoom: 14 });
  }, [map, key, large]);
  return null;
}

// Zemljevid ture: skladišče, oštevilčeni postanki in črta po vrstnem redu dostave
// Stran Sestavljanje ture doda še nerazporejena naročila in gumba za dodajanje v turo in odstranjevanje iz nje
// Če je podana črta po cestah (roadLine), jo narišemo namesto ravnih črt med postanki
export default function TourMap({
  warehouse, stops, orders = [], onAddOrder, onRemoveStop, large = false, roadLine = null,
}) {
  const located = stops.filter((stop) => stop.lat !== null && stop.lng !== null);
  const missing = stops.filter((stop) => stop.lat === null || stop.lng === null);
  const hasWarehouse = warehouse.lat !== null && warehouse.lng !== null;

  // Zaporedni postanki iste stranke so na istem naslovu, zato dobijo eno oznako, npr. 1–2
  const groups = groupStops(located);
  const start = hasWarehouse ? [[warehouse.lat, warehouse.lng]] : [];
  const points = [...start, ...groups.map((group) => [group.stops[0].lat, group.stops[0].lng])];

  // Naročila iste stranke so na istem naslovu, zato dobijo eno oznako
  const customers = [];
  for (const order of orders) {
    if (order.lat === null || order.lng === null) continue;
    const customer = customers.find((item) => item.id === order.customer_id);
    if (customer) customer.orders.push(order);
    else customers.push({ id: order.customer_id, orders: [order] });
  }
  // Pogled zajame turo in prikazana naročila, da nobena oznaka ne ostane zunaj zemljevida
  const visible = [...points, ...customers.map((customer) => [customer.orders[0].lat, customer.orders[0].lng])];

  return (
    <>
      {/* Velikost določa zunanji okvir, ker MapContainer po prvem izrisu razreda ne spremeni več */}
      <div className={large ? "tp-map tp-map-large" : "tp-map"}>
        <MapContainer center={[46.12, 14.82]} zoom={8} className="h-100 rounded">
          <TileLayer
            url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          />
          <FitPoints points={visible} large={large} />
          <Polyline positions={roadLine ?? points} pathOptions={{ color: "#4f8a63", weight: 3 }} />
          {hasWarehouse && (
            <Marker position={[warehouse.lat, warehouse.lng]} icon={markerIcon("S", "tp-map-warehouse")}>
              <Popup>
                <strong>Skladišče</strong>
                <br />
                {warehouse.address}
              </Popup>
            </Marker>
          )}
          {groups.map((group) => {
            const first = group.stops[0];
            const last = group.stops.at(-1);
            const label = first === last ? first.sequence : `${first.sequence}–${last.sequence}`;
            return (
              <Marker key={first.id} position={[first.lat, first.lng]} icon={markerIcon(label)}>
                <Popup>
                  <strong>{first.customer}</strong>
                  <br />
                  {first.address}, {first.city}
                  <br />
                  {!onRemoveStop && group.stops.map((stop) => stop.order_number).join(", ")}
                  {onRemoveStop &&
                    group.stops.map((stop) => (
                      <div key={stop.id} className="mt-2">
                        {stop.sequence}. {stop.order_number} · {formatNumber(stop.weight_kg)} kg ·{" "}
                        {formatNumber(stop.pallets)} pal.
                        <br />
                        <button className="btn btn-sm btn-outline-danger mt-1" onClick={() => onRemoveStop(stop)}>
                          Odstrani iz ture
                        </button>
                      </div>
                    ))}
                </Popup>
              </Marker>
            );
          })}
          {customers.map((customer) => {
            const first = customer.orders[0];
            // Stranka, ki že ima postanek v turi, dobi zamaknjeno oznako, da ne prekrije številke postanka
            const classes = [
              "tp-map-order",
              customer.orders.some((order) => order.is_late) && "tp-map-late",
              located.some((stop) => stop.customer_id === customer.id) && "tp-map-shifted",
            ];
            return (
              <Marker
                key={`customer-${customer.id}`}
                position={[first.lat, first.lng]}
                icon={markerIcon("+", classes.filter(Boolean).join(" "))}
              >
                <Popup>
                  <strong>{first.customer}</strong>
                  <br />
                  {first.city}
                  {customer.orders.map((order) => (
                    <div key={order.id} className="mt-2">
                      {order.number} · {formatNumber(order.weight_kg)} kg · {formatNumber(order.pallets)} pal.
                      <br />
                      rok {formatDate(order.dispatch_deadline)}
                      {order.is_late && " · po roku odpreme"}
                      <br />
                      <button className="btn btn-sm btn-primary mt-1" onClick={() => onAddOrder(order)}>
                        Dodaj v turo
                      </button>
                    </div>
                  ))}
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>
      {missing.length > 0 && (
        <div className="small text-warning-emphasis mt-2">
          ⚠ Postanki brez lokacije ({missing.length}):{" "}
          {missing.map((stop) => `${stop.sequence}. ${stop.customer} (${stop.order_number})`).join(", ")}
        </div>
      )}
    </>
  );
}
