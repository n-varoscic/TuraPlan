import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createTour, getTourOptions } from "../api/client.js";
import { todayIso } from "../format.js";

// Nova tura: datum odpreme, prosto vozilo in prost voznik
export default function NewTourPage() {
  const navigate = useNavigate();
  const [date, setDate] = useState(todayIso());
  const [options, setOptions] = useState({ vehicles: [], drivers: [] });
  const [vehicle, setVehicle] = useState("");
  const [driver, setDriver] = useState("");
  const [error, setError] = useState("");

  // Ob spremembi datuma naložimo vozila in voznike, ki ta dan še nimajo ture
  useEffect(() => {
    if (!date) return;
    getTourOptions(date)
      .then(setOptions)
      .catch((err) => setError(err.message));
  }, [date]);

  function changeDate(value) {
    setDate(value);
    setVehicle("");
    setDriver("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      const tour = await createTour({ dispatch_date: date, vehicle, driver });
      navigate(`/tours/${tour.id}/edit`, { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <Link to="/tours" className="small">← Seznam tur</Link>
      <h1 className="h3 mt-2 mb-3">Nova tura</h1>

      <form className="card p-4" onSubmit={handleSubmit}>
        <div className="row g-3">
          <div className="col-md-4">
            <label className="form-label" htmlFor="date">Datum odpreme</label>
            <input
              id="date"
              type="date"
              className="form-control"
              value={date}
              onChange={(e) => changeDate(e.target.value)}
              required
            />
          </div>
          <div className="col-md-4">
            <label className="form-label" htmlFor="vehicle">Vozilo</label>
            <select
              id="vehicle"
              className="form-select"
              value={vehicle}
              onChange={(e) => setVehicle(e.target.value)}
              required
            >
              <option value="">
                {options.vehicles.length ? "Izberi vozilo" : "Ni prostih vozil"}
              </option>
              {options.vehicles.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.registration_number} · {v.max_load_kg} kg · {v.pallet_spaces} pal.
                </option>
              ))}
            </select>
          </div>
          <div className="col-md-4">
            <label className="form-label" htmlFor="driver">Voznik</label>
            <select
              id="driver"
              className="form-select"
              value={driver}
              onChange={(e) => setDriver(e.target.value)}
              required
            >
              <option value="">
                {options.drivers.length ? "Izberi voznika" : "Ni prostih voznikov"}
              </option>
              {options.drivers.map((d) => (
                <option key={d.id} value={d.id}>{d.first_name} {d.last_name}</option>
              ))}
            </select>
          </div>
        </div>
        <p className="small text-muted mt-3 mb-0">
          Na voljo so samo aktivna vozila in vozniki, ki na izbrani datum še nimajo ture.
        </p>
        {error && <div className="alert alert-danger mt-3 mb-0">{error}</div>}
        <div className="mt-3">
          <button type="submit" className="btn btn-primary">Ustvari turo</button>
        </div>
      </form>
    </>
  );
}
