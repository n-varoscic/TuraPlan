import { formatNumber } from "../format.js";

// Zasedenost vozila: teža in palete glede na zmogljivost, npr. 980 / 1.200 kg · 3,5 / 4 pal.
export default function TourLoad({ tour }) {
  return (
    <span className="text-nowrap">
      {formatNumber(tour.total_weight_kg)} / {formatNumber(tour.vehicle.max_load_kg)} kg ·{" "}
      {formatNumber(tour.total_pallets)} / {tour.vehicle.pallet_spaces} pal.
    </span>
  );
}
