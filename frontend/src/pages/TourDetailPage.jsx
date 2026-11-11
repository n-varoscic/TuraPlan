import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getTour, getTourRoute, unconfirmTour } from "../api/client.js";
import DeliveryProgress from "../components/DeliveryProgress.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import TourLoad from "../components/TourLoad.jsx";
import TourMap from "../components/TourMap.jsx";
import { formatDate, formatDateTime, formatDuration, formatNumber } from "../format.js";
import { STOP_RESULT, TOUR_STATUS } from "../labels.js";

// Podrobnosti ture: podatki ture in vsi postanki z rezultatom dostave
export default function TourDetailPage() {
  const { id } = useParams();
  const [tour, setTour] = useState(null);
  // Pot ture po cestah; null, dokler se nalaga ali če storitev ni dosegljiva
  const [road, setRoad] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getTour(id)
      .then(setTour)
      .catch((err) => setError(err.message));
    // Brez poti po cestah zemljevid pokaže ravne črte, zato napake ne prikazujemo
    getTourRoute(id)
      .then((data) => setRoad(data.road))
      .catch(() => setRoad(null));
  }, [id]);

  async function unconfirm() {
    setError("");
    try {
      setTour(await unconfirmTour(tour.id));
    } catch (err) {
      setError(err.message);
    }
  }

  if (!tour) return error ? <div className="alert alert-danger">{error}</div> : <p className="text-muted">Nalagam …</p>;

  return (
    <>
      <Link to="/tours" className="small">← Seznam tur</Link>
      <div className="d-flex align-items-center gap-3 mt-2 mb-3">
        <h1 className="h3 mb-0">
          Tura {formatDate(tour.dispatch_date)} · {tour.vehicle.registration_number}
        </h1>
        <StatusBadge {...TOUR_STATUS[tour.status]} />
        {tour.status === "DRAFT" && (
          <Link to={`/tours/${tour.id}/edit`} className="btn btn-sm btn-primary ms-auto">Uredi turo</Link>
        )}
        {/* Potrjeno turo lahko disponent odklene, dokler je voznik ni začel */}
        {tour.status === "CONFIRMED" && (
          <button className="btn btn-sm btn-outline-primary ms-auto" onClick={unconfirm}>
            Vrni v osnutek
          </button>
        )}
      </div>
      {error && <div className="alert alert-danger">{error}</div>}

      <dl className="row mb-4">
        <dt className="col-sm-3">Voznik</dt>
        <dd className="col-sm-9">{tour.driver.first_name} {tour.driver.last_name}</dd>
        {tour.confirmed_at && (
          <>
            <dt className="col-sm-3">Potrjena</dt>
            <dd className="col-sm-9">{formatDateTime(tour.confirmed_at)}</dd>
          </>
        )}
        <dt className="col-sm-3">Zasedenost vozila</dt>
        <dd className="col-sm-9"><TourLoad tour={tour} /></dd>
        {road && (
          <>
            <dt className="col-sm-3">Pot po cestah</dt>
            <dd className="col-sm-9">
              {formatNumber(road.distance_km)} km · {formatDuration(road.duration_min)} vožnje
            </dd>
          </>
        )}
        <dt className="col-sm-3">Napredek dostav</dt>
        <dd className="col-sm-9"><DeliveryProgress tour={tour} /></dd>
      </dl>

      <div className="card p-2 mb-4">
        <TourMap warehouse={tour.warehouse} stops={tour.stops} roadLine={road?.geometry} />
      </div>

      <h2 className="h5">Postanki</h2>
      {tour.stops.length === 0 && <p className="text-muted">Tura še nima postankov.</p>}
      {tour.stops.length > 0 && (
        <div className="table-responsive">
          <table className="table align-middle">
            <thead className="table-light">
              <tr>
                <th>#</th>
                <th>Naročilo</th>
                <th>Stranka</th>
                <th>Naslov</th>
                <th>Teža</th>
                <th>Palete</th>
                <th>Rezultat</th>
                <th>Označeno ob</th>
                <th>Razlog nedostave</th>
              </tr>
            </thead>
            <tbody>
              {tour.stops.map((stop) => (
                <tr key={stop.id} className={stop.result === "NOT_DELIVERED" ? "table-danger" : ""}>
                  <td>{stop.sequence}</td>
                  <td>{stop.order_number}</td>
                  <td>
                    {stop.customer}
                    {stop.delivery_note && <div className="small text-info-emphasis">📌 {stop.delivery_note}</div>}
                    {stop.driver_note && <div className="small text-muted">{stop.driver_note}</div>}
                  </td>
                  <td>{stop.address}, {stop.city}</td>
                  <td className="text-nowrap">{formatNumber(stop.weight_kg)} kg</td>
                  <td>{formatNumber(stop.pallets)}</td>
                  <td><StatusBadge {...STOP_RESULT[stop.result]} /></td>
                  <td className="text-nowrap">{formatDateTime(stop.marked_at)}</td>
                  <td>{stop.reason || "–"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
