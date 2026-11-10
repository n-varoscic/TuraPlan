import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { addStop, getOrders, getTour, removeStop } from "../api/client.js";
import StatusBadge from "../components/StatusBadge.jsx";
import TourLoad from "../components/TourLoad.jsx";
import { formatDate, formatNumber } from "../format.js";
import { TOUR_STATUS } from "../labels.js";

// Sestavljanje ture: levo nerazporejena naročila, desno postanki ture
export default function TourBuilderPage() {
  const { id } = useParams();
  const [tour, setTour] = useState(null);
  const [orders, setOrders] = useState([]);
  const [region, setRegion] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getTour(id)
      .then(async (data) => {
        setTour(data);
        setOrders(await getOrders(data.dispatch_date));
      })
      .catch((err) => setError(err.message));
  }, [id]);

  // Po dodajanju ali odstranjevanju prikažemo novo turo in osvežimo nerazporejena naročila
  async function update(action) {
    setError("");
    try {
      const updated = await action();
      setTour(updated);
      setOrders(await getOrders(updated.dispatch_date));
    } catch (err) {
      setError(err.message);
    }
  }

  if (!tour) return error ? <div className="alert alert-danger">{error}</div> : <p className="text-muted">Nalagam …</p>;

  const regions = [...new Set(orders.map((order) => order.region))].sort();
  const shownOrders = region ? orders.filter((order) => order.region === region) : orders;

  return (
    <>
      <Link to="/tours" className="small">← Seznam tur</Link>
      <div className="d-flex align-items-center gap-3 mt-2 mb-1">
        <h1 className="h3 mb-0">Sestavljanje ture</h1>
        <StatusBadge {...TOUR_STATUS[tour.status]} />
        <Link to={`/tours/${tour.id}`} className="btn btn-sm btn-outline-primary ms-auto">Podrobnosti</Link>
      </div>
      <p className="text-muted mb-3">
        {formatDate(tour.dispatch_date)} · {tour.vehicle.registration_number} · {tour.driver.first_name}{" "}
        {tour.driver.last_name}
      </p>

      <div className="card px-4 py-3 mb-3">
        <div>Zasedenost vozila: <TourLoad tour={tour} /></div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="row g-3">
        <div className="col-lg-5">
          <div className="card h-100">
            <div className="card-header d-flex align-items-center gap-2">
              <h2 className="h6 mb-0 flex-grow-1">Nerazporejena naročila</h2>
              <select
                className="form-select form-select-sm w-auto"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                aria-label="Regija"
              >
                <option value="">Vse regije</option>
                {regions.map((name) => <option key={name} value={name}>{name}</option>)}
              </select>
            </div>
            <ul className="list-group list-group-flush tp-scroll-list">
              {shownOrders.length === 0 && <li className="list-group-item text-muted">Ni naročil.</li>}
              {shownOrders.map((order) => (
                <li key={order.id} className="list-group-item d-flex align-items-center gap-2">
                  <div className="flex-grow-1">
                    <div>
                      {order.customer} <span className="small text-muted">· {order.number}</span>
                    </div>
                    <div className="small text-muted">
                      {order.city} · {formatNumber(order.weight_kg)} kg · {formatNumber(order.pallets)} pal. ·
                      rok {formatDate(order.dispatch_deadline)}
                    </div>
                    {order.status === "NOT_DELIVERED" && (
                      <span className="badge bg-danger-subtle text-danger-emphasis mt-1">ponovna dostava</span>
                    )}
                  </div>
                  {order.is_late && (
                    <span className="badge bg-warning-subtle text-warning-emphasis border border-warning-subtle">
                      ⚠ po roku odpreme
                    </span>
                  )}
                  <button
                    className="btn btn-sm btn-outline-primary"
                    onClick={() => update(() => addStop(tour.id, order.id))}
                    aria-label={`Dodaj ${order.number} v turo`}
                  >
                    +
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="col-lg-7">
          <div className="card h-100">
            <div className="card-header">
              <h2 className="h6 mb-0">Postanki ({tour.stops.length})</h2>
            </div>
            <ul className="list-group list-group-flush tp-scroll-list">
              {tour.stops.length === 0 && (
                <li className="list-group-item text-muted">Dodaj naročila s seznama na levi.</li>
              )}
              {tour.stops.map((stop) => (
                <li key={stop.id} className="list-group-item d-flex align-items-center gap-3">
                  <span className="tp-sequence">{stop.sequence}</span>
                  <div className="flex-grow-1">
                    <div>
                      {stop.customer} <span className="small text-muted">· {stop.order_number}</span>
                    </div>
                    <div className="small text-muted">
                      {stop.address}, {stop.city} · {formatNumber(stop.weight_kg)} kg ·{" "}
                      {formatNumber(stop.pallets)} pal.
                    </div>
                  </div>
                  <button
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => update(() => removeStop(stop.id))}
                    aria-label={`Odstrani ${stop.order_number} iz ture`}
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </>
  );
}
