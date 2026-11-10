import { formatNumber, formatPallets } from "../format.js";

// Zasedenost vozila: teža in palete glede na zmogljivost, npr. 980 / 1.200 kg · 3,5 / 4 pal.
// Presežena vrednost je rdeča, z showWarnings pa so pod njo še opozorila, za koliko je presežena
export default function TourLoad({ tour, showWarnings = false }) {
  const weightOver = Number(tour.weight_exceeded_by) > 0;
  const palletsOver = Number(tour.pallets_exceeded_by) > 0;

  return (
    <>
      <span className="text-nowrap">
        <span className={weightOver ? "text-danger-emphasis fw-semibold" : undefined}>
          {formatNumber(tour.total_weight_kg)} / {formatNumber(tour.vehicle.max_load_kg)} kg
        </span>{" "}
        ·{" "}
        <span className={palletsOver ? "text-danger-emphasis fw-semibold" : undefined}>
          {formatNumber(tour.total_pallets)} / {tour.vehicle.pallet_spaces} pal.
        </span>
      </span>
      {showWarnings && weightOver && (
        <div className="small text-danger-emphasis">⚠ Preseženo za {formatNumber(tour.weight_exceeded_by)} kg</div>
      )}
      {showWarnings && palletsOver && (
        <div className="small text-danger-emphasis">⚠ Preseženo za {formatPallets(tour.pallets_exceeded_by)}</div>
      )}
    </>
  );
}
