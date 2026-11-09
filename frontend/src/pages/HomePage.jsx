import { useEffect, useState } from "react";
import { getHealth } from "../api/client.js";

// Začasna začetna stran, ki preveri povezavo z backendom
export default function HomePage() {
  // null = še preverjamo, true = backend dosegljiv, false = ni dosegljiv
  const [backendOk, setBackendOk] = useState(null);

  // Ob prvem prikazu strani pokliče /api/health/
  useEffect(() => {
    getHealth()
      .then(() => setBackendOk(true))
      .catch(() => setBackendOk(false));
  }, []);

  return (
    <>
      <h1 className="h3 mb-3">Planiranje dostavnih tur</h1>
      {backendOk === null && <div className="alert alert-secondary">Preverjam povezavo z backendom …</div>}
      {backendOk === true && <div className="alert alert-success">Backend je dosegljiv.</div>}
      {backendOk === false && <div className="alert alert-danger">Backend ni dosegljiv.</div>}
    </>
  );
}
