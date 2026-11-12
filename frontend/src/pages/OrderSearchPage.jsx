import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { searchOrders } from "../api/client.js";
import OrderSearch from "../components/OrderSearch.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import { formatDate } from "../format.js";
import { ORDER_STATUS } from "../labels.js";

// Zadetki iskanja naročil: status naročila, tura in razlog zadnje nedostave
export default function OrderSearchPage() {
  // Iskano besedilo je v naslovu strani (?q=…), zato zadetki ostanejo tudi po osvežitvi
  const [params] = useSearchParams();
  const query = params.get("q") ?? "";
  // null pomeni, da se zadetki še nalagajo
  const [orders, setOrders] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    // Odgovor za prejšnje iskanje zavržemo, če je disponent medtem iskal nekaj drugega
    let current = true;
    searchOrders(query)
      .then((data) => {
        if (!current) return;
        setError("");
        setOrders(data);
      })
      .catch((err) => current && setError(err.message));
    return () => {
      current = false;
    };
  }, [query]);

  return (
    <>
      <Link to="/tours" className="small">← Seznam tur</Link>
      <h1 className="h3 mt-2">Iskanje naročila</h1>
      {/* Novo iskanje je mogoče tudi neposredno s strani z zadetki */}
      <div className="row mb-3">
        <div className="col-sm-6 col-lg-4">
          <OrderSearch />
        </div>
      </div>
      <p className="text-muted">
        Iskano: »{query}« · številka naročila se mora ujemati v celoti, za naziv stranke vpiši vsaj 3 znake
      </p>

      {error && <div className="alert alert-danger">{error}</div>}
      {!error && orders === null && <p className="text-muted">Nalagam …</p>}
      {orders !== null && orders.length === 0 && <div className="alert alert-secondary">Ni najdenih naročil</div>}
      {orders !== null && orders.length > 0 && (
        <div className="card table-responsive">
          <table className="table align-middle mb-0">
            <thead className="table-light">
              <tr>
                <th>Naročilo</th>
                <th>Stranka</th>
                <th>Rok odpreme</th>
                <th>Status</th>
                <th>Tura</th>
                <th>Razlog nedostave</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.id}>
                  <td>{order.number}</td>
                  <td>
                    {order.customer} <span className="small text-muted">· {order.city}</span>
                  </td>
                  <td>{formatDate(order.dispatch_deadline)}</td>
                  <td><StatusBadge {...ORDER_STATUS[order.status]} /></td>
                  <td>
                    {order.tour ? (
                      <Link to={`/tours/${order.tour.id}`}>
                        {formatDate(order.tour.dispatch_date)} · {order.tour.driver}
                      </Link>
                    ) : (
                      "–"
                    )}
                  </td>
                  <td>{order.not_delivered_reason || "–"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
