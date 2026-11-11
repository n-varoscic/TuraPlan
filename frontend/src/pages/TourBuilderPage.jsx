import { useEffect, useState } from "react";
import { Link, Navigate, useParams } from "react-router-dom";
import {
  addStop, changeVehicle, confirmTour, getOrders, getTour, getTourOptions, moveStop, moveStopTo, removeStop,
  updateDeliveryNote, updateDriverNote,
} from "../api/client.js";
import DriverNoteInput from "../components/DriverNoteInput.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import TourLoad from "../components/TourLoad.jsx";
import TourMap from "../components/TourMap.jsx";
import { formatDate, formatNumber, pluralize } from "../format.js";
import { TOUR_STATUS } from "../labels.js";
import { groupStops } from "../stopGroups.js";

// Sestavljanje ture: levo nerazporejena naročila, desno postanki ture
export default function TourBuilderPage() {
  const { id } = useParams();
  const [tour, setTour] = useState(null);
  const [orders, setOrders] = useState([]);
  const [freeVehicles, setFreeVehicles] = useState([]);
  // Postanek, ki ga disponent vleče, in mesto, nad katerim je trenutno
  const [dragged, setDragged] = useState(null);
  const [dropSequence, setDropSequence] = useState(null);
  // Postanek, ki ga je mogoče vleči; ob kliku v polje ali gumb ga izklopimo, da označevanje besedila deluje
  const [draggableId, setDraggableId] = useState(null);
  const [region, setRegion] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getTour(id)
      .then(async (data) => {
        setTour(data);
        setOrders(await getOrders(data.dispatch_date));
        setFreeVehicles((await getTourOptions(data.dispatch_date)).vehicles);
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

  function endDrag() {
    setDragged(null);
    setDropSequence(null);
  }

  // Spuščen postanek zasede mesto postanka, na katerega ga disponent spusti
  function dropOn(position) {
    const stop = dragged;
    endDrag();
    if (stop && stop.sequence !== position) update(() => moveStopTo(stop.id, position));
  }

  // Črta nad ali pod postankom pokaže, kam bo spuščen postanek prišel
  function dropClass(stop) {
    if (!dragged || dropSequence !== stop.sequence || dragged.id === stop.id) return "";
    return dragged.sequence > stop.sequence ? "tp-drop-before" : "tp-drop-after";
  }

  // Po menjavi vozila je prejšnje vozilo spet prosto, zato osvežimo tudi seznam vozil
  async function selectVehicle(vehicleId) {
    setError("");
    try {
      const updated = await changeVehicle(tour.id, vehicleId);
      const options = await getTourOptions(tour.dispatch_date);
      setTour(updated);
      setFreeVehicles(options.vehicles);
    } catch (err) {
      setError(err.message);
    }
  }

  if (!tour) return error ? <div className="alert alert-danger">{error}</div> : <p className="text-muted">Nalagam …</p>;
  // Potrjena tura je zaklenjena, zato namesto urejanja prikažemo njene podrobnosti
  if (tour.status !== "DRAFT") return <Navigate to={`/tours/${tour.id}`} replace />;

  const regions = [...new Set(orders.map((order) => order.region))].sort();
  const shownOrders = region ? orders.filter((order) => order.region === region) : orders;
  const groups = groupStops(tour.stops);
  const lastSequence = tour.stops.length;

  // Trenutno vozilo ture in vozila, ki so na ta datum še prosta
  const otherVehicles = freeVehicles.filter((vehicle) => vehicle.id !== tour.vehicle.id);
  const vehicles = [tour.vehicle, ...otherVehicles].sort((a, b) =>
    a.registration_number.localeCompare(b.registration_number),
  );

  return (
    <>
      <Link to="/tours" className="small">← Seznam tur</Link>
      <div className="d-flex align-items-center gap-3 mt-2 mb-1">
        <h1 className="h3 mb-0">Sestavljanje ture</h1>
        <StatusBadge {...TOUR_STATUS[tour.status]} />
        {/* Spremembe se shranjujejo ob vsakem kliku, zato gumb samo zapre urejanje */}
        <span className="small text-muted ms-auto">Spremembe se shranjujejo sproti</span>
        <Link to={`/tours/${tour.id}`} className="btn btn-sm btn-outline-primary">Končaj urejanje</Link>
        <button
          className="btn btn-sm btn-primary"
          onClick={() => update(() => confirmTour(tour.id))}
          disabled={tour.confirmation_errors.length > 0}
        >
          Potrdi turo
        </button>
      </div>
      {tour.confirmation_errors.length > 0 && (
        <div className="small text-muted text-end mb-1">
          Potrditev ni mogoča: {tour.confirmation_errors.join(" · ")}
        </div>
      )}
      <p className="text-muted mb-3">
        {formatDate(tour.dispatch_date)} · {tour.driver.first_name} {tour.driver.last_name}
      </p>

      <div className="card px-4 py-3 mb-3">
        <div className="row g-3 align-items-center">
          <div className="col-auto">
            <label htmlFor="vehicle" className="form-label small text-muted mb-1">Vozilo</label>
            <select
              id="vehicle"
              className="form-select form-select-sm"
              value={tour.vehicle.id}
              onChange={(e) => selectVehicle(Number(e.target.value))}
              disabled={tour.status !== "DRAFT"}
            >
              {vehicles.map((vehicle) => (
                <option key={vehicle.id} value={vehicle.id}>
                  {vehicle.registration_number} · {formatNumber(vehicle.max_load_kg)} kg ·{" "}
                  {vehicle.pallet_spaces} pal.
                </option>
              ))}
            </select>
          </div>
          <div className="col">
            <div className="small text-muted mb-1">Zasedenost vozila</div>
            <TourLoad tour={tour} showWarnings />
          </div>
        </div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="row g-3">
        <div className="col-lg-5 d-flex flex-column gap-3">
          {/* Zemljevid se izriše iz postankov ture, zato se ob vsaki spremembi vrstnega reda takoj posodobi */}
          <div className="card p-2">
            <TourMap warehouse={tour.warehouse} stops={tour.stops} />
          </div>
          <div className="card flex-grow-1">
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
            {tour.split_customers.length > 0 && (
              <div className="alert alert-warning small rounded-0 border-0 border-bottom mb-0 py-2">
                ⚠ Postanki iste stranke niso zaporedni: {tour.split_customers.join(", ")}
              </div>
            )}
            <ul className="list-group list-group-flush tp-scroll-list">
              {tour.stops.length === 0 && (
                <li className="list-group-item text-muted">Dodaj naročila s seznama na levi.</li>
              )}
              {groups.map((group) => {
                const grouped = group.stops.length > 1;
                return [
                  grouped && (
                    <li key={`group-${group.stops[0].id}`} className="list-group-item tp-customer-group py-1 small">
                      {group.customer} – {pluralize(group.stops.length, ["naročilo", "naročili", "naročila", "naročil"])}
                    </li>
                  ),
                  ...group.stops.map((stop) => (
                    <li
                      key={stop.id}
                      className={[
                        "list-group-item d-flex align-items-start gap-2 tp-draggable",
                        grouped && "tp-customer-group",
                        dragged?.id === stop.id && "tp-dragging",
                        dropClass(stop),
                      ].filter(Boolean).join(" ")}
                      draggable={draggableId === stop.id}
                      onMouseDown={(e) => {
                        setDraggableId(e.target.closest("input, button") ? null : stop.id);
                      }}
                      onDragStart={(e) => {
                        e.dataTransfer.effectAllowed = "move";
                        setDragged(stop);
                      }}
                      onDragEnd={endDrag}
                      onDragOver={(e) => {
                        if (!dragged) return;
                        e.preventDefault();
                        setDropSequence(stop.sequence);
                      }}
                      onDrop={(e) => {
                        e.preventDefault();
                        dropOn(stop.sequence);
                      }}
                    >
                      <span className="tp-drag-handle mt-1" title="Povleci na novo mesto" aria-hidden="true">
                        ⠿
                      </span>
                      <span className="tp-sequence mt-1">{stop.sequence}</span>
                      <div className="flex-grow-1">
                        <div>
                          {stop.customer} <span className="small text-muted">· {stop.order_number}</span>
                        </div>
                        <div className="small text-muted">
                          {stop.address}, {stop.city} · {formatNumber(stop.weight_kg)} kg ·{" "}
                          {formatNumber(stop.pallets)} pal.
                        </div>
                        {stop.lat === null && (
                          <div className="small text-warning-emphasis">⚠ Lokacija ni določena</div>
                        )}
                        {stop.delivery_note && (
                          <div className="small text-info-emphasis mt-1">
                            📌 Stalna opomba: {stop.delivery_note}{" "}
                            <button
                              type="button"
                              className="btn btn-link btn-sm p-0 small align-baseline"
                              onClick={() => update(() => updateDeliveryNote(stop.id, ""))}
                            >
                              odstrani
                            </button>
                          </div>
                        )}
                        <DriverNoteInput
                          // Ob spremembi shranjenih opomb se polje ponastavi na shranjeno opombo za voznika
                          key={`${stop.id}-${stop.driver_note}-${stop.delivery_note}`}
                          stop={stop}
                          onSave={(note) => update(() => updateDriverNote(stop.id, note))}
                          onSaveAsDeliveryNote={(note) => update(() => updateDeliveryNote(stop.id, note))}
                        />
                      </div>
                      <div className="d-flex gap-1">
                        <button
                          className="btn btn-sm btn-outline-primary"
                          onClick={() => update(() => moveStop(stop.id, "up"))}
                          disabled={stop.sequence === 1}
                          aria-label={`Premakni ${stop.order_number} gor`}
                        >
                          ↑
                        </button>
                        <button
                          className="btn btn-sm btn-outline-primary"
                          onClick={() => update(() => moveStop(stop.id, "down"))}
                          disabled={stop.sequence === lastSequence}
                          aria-label={`Premakni ${stop.order_number} dol`}
                        >
                          ↓
                        </button>
                        <button
                          className="btn btn-sm btn-outline-danger"
                          onClick={() => update(() => removeStop(stop.id))}
                          aria-label={`Odstrani ${stop.order_number} iz ture`}
                        >
                          ×
                        </button>
                      </div>
                    </li>
                  )),
                ];
              })}
            </ul>
          </div>
        </div>
      </div>
    </>
  );
}
