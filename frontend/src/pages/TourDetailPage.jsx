import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getTour } from "../api/client.js";
import DeliveryProgress from "../components/DeliveryProgress.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import TourLoad from "../components/TourLoad.jsx";
import { formatDate, formatDateTime, formatNumber } from "../format.js";
import { STOP_RESULT, TOUR_STATUS } from "../labels.js";

// Podrobnosti ture: podatki ture in vsi postanki z rezultatom dostave
export default function TourDetailPage() {
  const { id } = useParams();
  const [tour, setTour] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getTour(id)
      .then(setTour)
      .catch((err) => setError(err.message));
  }, [id]);

  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!tour) return <p className="text-muted">Nalagam …</p>;

  return (
    <>
      <Link to="/tours" className="small">← Seznam tur</Link>
      <div className="d-flex align-items-center gap-3 mt-2 mb-3">
        <h1 className="h3 mb-0">
          Tura {formatDate(tour.dispatch_date)} · {tour.vehicle.registration_number}
        </h1>
        <StatusBadge {...TOUR_STATUS[tour.status]} />
        {tour.status === "DRAFT" && (
          <Link to={`/tours/${tour.id}/edit`} className="btn btn-sm btn-primary ms-auto">Sestavi turo</Link>
        )}
      </div>

      <dl className="row mb-4">
        <dt className="col-sm-3">Voznik</dt>
        <dd className="col-sm-9">{tour.driver.first_name} {tour.driver.last_name}</dd>
        <dt className="col-sm-3">Zasedenost vozila</dt>
        <dd className="col-sm-9"><TourLoad tour={tour} /></dd>
        <dt className="col-sm-3">Napredek dostav</dt>
        <dd className="col-sm-9"><DeliveryProgress tour={tour} /></dd>
      </dl>

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
