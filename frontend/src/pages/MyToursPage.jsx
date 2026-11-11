import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMyTours } from "../api/client.js";
import DeliveryProgress from "../components/DeliveryProgress.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import { formatDate, pluralize } from "../format.js";
import { TOUR_STATUS } from "../labels.js";

const STOPS = ["postanek", "postanka", "postanki", "postankov"];

// Začetna stran voznika: njegove potrjene, začete in zaključene ture, najnovejše zgoraj
export default function MyToursPage() {
  const [tours, setTours] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getMyTours()
      .then(setTours)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!tours) return <p className="text-muted">Nalagam …</p>;

  return (
    <>
      <h1 className="h3 mb-3">Moje ture</h1>
      {tours.length === 0 && <p className="text-muted">Nimaš potrjenih tur.</p>}
      <div className="d-flex flex-column gap-2">
        {tours.map((tour) => (
          <Link key={tour.id} to={`/my-tours/${tour.id}`} className="card tp-card-link text-reset text-decoration-none">
            <div className="card-body py-3">
              <div className="d-flex align-items-center gap-2 mb-1">
                <span className="fw-medium">{formatDate(tour.dispatch_date)}</span>
                <StatusBadge {...TOUR_STATUS[tour.status]} />
              </div>
              <div className="small text-muted mb-2">
                {tour.vehicle.registration_number} · {pluralize(tour.stop_count, STOPS)}
              </div>
              <DeliveryProgress tour={tour} />
            </div>
          </Link>
        ))}
      </div>
    </>
  );
}
