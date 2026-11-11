import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { completeTour, getTour, markStop, startTour } from "../api/client.js";
import DeliveryProgress from "../components/DeliveryProgress.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import { formatDate, formatDateTime, formatNumber, pluralize } from "../format.js";
import { STOP_RESULT, TOUR_STATUS } from "../labels.js";
import { groupStops } from "../stopGroups.js";

// Tura voznika na telefonu: postanki po vrstnem redu, začetek ture, označevanje dostav in zaključek
export default function MyTourPage() {
  const { id } = useParams();
  const [tour, setTour] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getTour(id)
      .then(setTour)
      .catch((err) => setError(err.message));
  }, [id]);

  async function update(action) {
    setError("");
    try {
      setTour(await action());
    } catch (err) {
      setError(err.message);
    }
  }

  function complete() {
    // Po zaključku oznak ni več mogoče popraviti, zato voznik zaključek še enkrat potrdi
    if (window.confirm("Zaključim turo? Oznak postankov potem ni več mogoče spremeniti.")) {
      update(() => completeTour(tour.id));
    }
  }

  if (!tour) return error ? <div className="alert alert-danger">{error}</div> : <p className="text-muted">Nalagam …</p>;

  const inDelivery = tour.status === "IN_DELIVERY";

  return (
    <>
      <Link to="/my-tours" className="small">← Moje ture</Link>
      <div className="d-flex align-items-center gap-2 mt-2">
        <h1 className="h3 mb-0">Tura {formatDate(tour.dispatch_date)}</h1>
        <StatusBadge {...TOUR_STATUS[tour.status]} />
      </div>
      <p className="text-muted mb-2">
        {tour.vehicle.registration_number} · {formatNumber(tour.total_weight_kg)} kg ·{" "}
        {formatNumber(tour.total_pallets)} pal.
      </p>
      <div className="mb-3"><DeliveryProgress tour={tour} /></div>

      {tour.status === "CONFIRMED" && (
        <div className="mb-3">
          <button
            className="btn btn-primary w-100"
            onClick={() => update(() => startTour(tour.id))}
            disabled={tour.start_errors.length > 0}
          >
            Začni turo
          </button>
          {tour.start_errors.map((reason) => (
            <div key={reason} className="small text-muted mt-1">{reason}</div>
          ))}
        </div>
      )}

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="d-flex flex-column gap-2">
        {groupStops(tour.stops).map((group) => (
          <div key={group.stops[0].id} className={group.stops.length > 1 ? "tp-customer-group rounded p-2" : ""}>
            {group.stops.length > 1 && (
              <div className="small mb-2">
                {group.customer} – {pluralize(group.stops.length, ["naročilo", "naročili", "naročila", "naročil"])}
              </div>
            )}
            <div className="d-flex flex-column gap-2">
              {group.stops.map((stop) => (
                <StopCard
                  key={stop.id}
                  stop={stop}
                  canMark={inDelivery}
                  onMark={(result, reason) => update(() => markStop(stop.id, result, reason))}
                />
              ))}
            </div>
          </div>
        ))}
      </div>

      {inDelivery && (
        <div className="d-grid d-sm-flex justify-content-sm-end align-items-center gap-2 mt-4">
          {tour.complete_errors.map((reason) => (
            <span key={reason} className="small text-muted text-center">{reason}</span>
          ))}
          <button className="btn btn-primary" onClick={complete} disabled={tour.complete_errors.length > 0}>
            Zaključi turo
          </button>
        </div>
      )}
    </>
  );
}

// En postanek: podatki za dostavo, gumba za označitev in popravek oznake, dokler je tura v dostavi
function StopCard({ stop, canMark, onMark }) {
  const [editing, setEditing] = useState(false);
  const [askReason, setAskReason] = useState(false);
  const [reason, setReason] = useState(stop.reason);
  const pending = stop.result === "PENDING";
  const showButtons = canMark && (pending || editing);

  function mark(result, text = "") {
    setEditing(false);
    setAskReason(false);
    onMark(result, text);
  }

  return (
    <div className="card">
      <div className="card-body p-3">
        <div className="d-flex align-items-start gap-2">
          <span className="tp-sequence">{stop.sequence}</span>
          <div className="flex-grow-1 tp-min-w-0">
            <div className="fw-medium">{stop.customer}</div>
            <div className="small">{stop.address}, {stop.city}</div>
            {stop.phone && (
              <a href={`tel:${stop.phone.replace(/\s/g, "")}`} className="small">📞 {stop.phone}</a>
            )}
            <div className="small text-muted">
              {stop.order_number} · {formatNumber(stop.pallets)} pal. · {formatNumber(stop.weight_kg)} kg
            </div>
            {stop.delivery_note && <div className="small text-info-emphasis mt-1">📌 {stop.delivery_note}</div>}
            {stop.driver_note && <div className="small mt-1">💬 {stop.driver_note}</div>}
          </div>
        </div>

        {!pending && (
          <div className="d-flex align-items-start gap-2 mt-2 small">
            <div className="flex-grow-1">
              <StatusBadge {...STOP_RESULT[stop.result]} /> {formatDateTime(stop.marked_at)}
              {stop.reason && <div className="text-danger-emphasis mt-1">Razlog: {stop.reason}</div>}
            </div>
            {canMark && !editing && (
              <button className="btn btn-sm btn-outline-primary" onClick={() => setEditing(true)}>
                Uredi
              </button>
            )}
          </div>
        )}

        {showButtons && !askReason && (
          <div className="d-flex gap-2 mt-3">
            <button className="btn btn-success flex-fill" onClick={() => mark("DELIVERED")}>
              Dostavljeno
            </button>
            <button className="btn btn-outline-danger flex-fill" onClick={() => setAskReason(true)}>
              Ni dostavljeno
            </button>
            {editing && (
              <button className="btn btn-outline-secondary" onClick={() => setEditing(false)} aria-label="Prekliči">
                ×
              </button>
            )}
          </div>
        )}

        {showButtons && askReason && (
          <form
            className="mt-3"
            onSubmit={(e) => {
              e.preventDefault();
              mark("NOT_DELIVERED", reason);
            }}
          >
            <label htmlFor={`reason-${stop.id}`} className="form-label small">Razlog nedostave</label>
            <input
              id={`reason-${stop.id}`}
              className="form-control mb-2"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="npr. stranka zaprta"
              required
              autoFocus
            />
            <div className="d-flex gap-2">
              <button type="submit" className="btn btn-danger flex-fill" disabled={!reason.trim()}>
                Potrdi nedostavo
              </button>
              <button type="button" className="btn btn-outline-secondary" onClick={() => setAskReason(false)}>
                Prekliči
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
