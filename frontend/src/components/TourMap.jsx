import { useEffect } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { MapContainer, Marker, Polyline, Popup, TileLayer, useMap } from "react-leaflet";
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
function FitPoints({ points }) {
  const map = useMap();
  // Besedilo se spremeni samo, ko se spremenijo točke, zato se pogled ne premika brez razloga
  const key = JSON.stringify(points);
  useEffect(() => {
    const bounds = JSON.parse(key);
    if (bounds.length > 0) map.fitBounds(bounds, { padding: [30, 30], maxZoom: 14 });
  }, [map, key]);
  return null;
}

// Zemljevid ture: skladišče, oštevilčeni postanki in črta po vrstnem redu dostave
export default function TourMap({ warehouse, stops }) {
  const located = stops.filter((stop) => stop.lat !== null && stop.lng !== null);
  const missing = stops.filter((stop) => stop.lat === null || stop.lng === null);
  const hasWarehouse = warehouse.lat !== null && warehouse.lng !== null;

  // Zaporedni postanki iste stranke so na istem naslovu, zato dobijo eno oznako, npr. 1–2
  const groups = groupStops(located);
  const start = hasWarehouse ? [[warehouse.lat, warehouse.lng]] : [];
  const points = [...start, ...groups.map((group) => [group.stops[0].lat, group.stops[0].lng])];

  return (
    <>
      <MapContainer center={[46.12, 14.82]} zoom={8} className="tp-map">
        <TileLayer
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        <FitPoints points={points} />
        <Polyline positions={points} pathOptions={{ color: "#4f8a63", weight: 3 }} />
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
                {group.stops.map((stop) => stop.order_number).join(", ")}
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
      {missing.length > 0 && (
        <div className="small text-warning-emphasis mt-2">
          ⚠ Postanki brez lokacije ({missing.length}):{" "}
          {missing.map((stop) => `${stop.sequence}. ${stop.customer} (${stop.order_number})`).join(", ")}
        </div>
      )}
    </>
  );
}
