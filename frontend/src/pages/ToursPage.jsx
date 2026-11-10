import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { getTours } from "../api/client.js";
import DateRangePicker from "../components/DateRangePicker.jsx";
import DeliveryProgress from "../components/DeliveryProgress.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import TourLoad from "../components/TourLoad.jsx";
import { formatDate, todayIso } from "../format.js";
import { TOUR_STATUS } from "../labels.js";

// Osnutek se odpre za sestavljanje, ostale ture na podrobnostih
function tourPath(tour) {
  return tour.status === "DRAFT" ? `/tours/${tour.id}/edit` : `/tours/${tour.id}`;
}

// Začetna stran disponenta: vse ture s statusom, zasedenostjo in napredkom dostav
export default function ToursPage() {
  const navigate = useNavigate();
  // Filtre hranimo v naslovu strani (?date_from=…), da ostanejo tudi po vrnitvi s podrobnosti
  const [searchParams, setSearchParams] = useSearchParams();
  // Brez izbire so prikazane ture od danes naprej, prazno polje »Od« pomeni vse datume
  const dateFrom = searchParams.get("date_from") ?? todayIso();
  const dateTo = searchParams.get("date_to") ?? "";
  const status = searchParams.get("status") ?? "";
  const [tours, setTours] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getTours({ date_from: dateFrom, date_to: dateTo, status })
      .then(setTours)
      .catch((err) => setError(err.message));
  }, [dateFrom, dateTo, status]);

  function setFilter(name, value) {
    const params = new URLSearchParams(searchParams);
    params.set(name, value);
    setSearchParams(params);
  }

  function setDates(from, to) {
    const params = new URLSearchParams(searchParams);
    params.set("date_from", from);
    params.set("date_to", to);
    setSearchParams(params);
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1 className="h3 mb-0">Seznam tur</h1>
        <Link to="/tours/new" className="btn btn-primary">+ Nova tura</Link>
      </div>

      <div className="row g-2 mb-3 align-items-end">
        <div className="col-auto">
          <label className="form-label small text-muted">Datum odpreme</label>
          <DateRangePicker from={dateFrom} to={dateTo} onChange={setDates} />
        </div>
        <div className="col-auto">
          <button className="btn btn-outline-primary" onClick={() => setDates("", "")} disabled={!dateFrom && !dateTo}>
            Vsi datumi
          </button>
        </div>
        <div className="col-sm-3 col-lg-2">
          <label className="form-label small text-muted" htmlFor="status">Status</label>
          <select
            id="status"
            className="form-select"
            value={status}
            onChange={(e) => setFilter("status", e.target.value)}
          >
            <option value="">Vsi statusi</option>
            {Object.entries(TOUR_STATUS).map(([value, { label }]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}
      {tours?.length === 0 && <p className="text-muted">Ni tur za izbrane filtre.</p>}

      {tours?.length > 0 && (
        <div className="table-responsive">
          <table className="table table-hover align-middle text-nowrap">
            <thead className="table-light">
              <tr>
                <th>Datum odpreme</th>
                <th>Vozilo</th>
                <th>Voznik</th>
                <th>Postanki</th>
                <th>Zasedenost vozila</th>
                <th>Status</th>
                <th>Napredek dostav</th>
              </tr>
            </thead>
            <tbody>
              {tours.map((tour) => (
                <tr key={tour.id} role="button" onClick={() => navigate(tourPath(tour))}>
                  <td>{formatDate(tour.dispatch_date)}</td>
                  <td>{tour.vehicle.registration_number}</td>
                  <td>{tour.driver.first_name} {tour.driver.last_name}</td>
                  <td>{tour.stop_count}</td>
                  <td><TourLoad tour={tour} /></td>
                  <td><StatusBadge {...TOUR_STATUS[tour.status]} /></td>
                  <td><DeliveryProgress tour={tour} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
