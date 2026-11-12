import { useState } from "react";
import { useNavigate } from "react-router-dom";

// Iskalno polje za naročila: ob potrditvi odpre stran z zadetki
export default function OrderSearch() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  function submit(event) {
    // Brskalnik bi ob oddaji obrazca stran naložil znova, zato to preprečimo
    event.preventDefault();
    if (query.trim()) navigate(`/orders/search?q=${encodeURIComponent(query.trim())}`);
  }

  return (
    <form role="search" onSubmit={submit}>
      <label className="form-label small text-muted" htmlFor="order-search">Iskanje naročila</label>
      <div className="d-flex gap-2">
        <input
          id="order-search"
          type="search"
          className="form-control"
          placeholder="Številka naročila ali stranka"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="btn btn-outline-primary">Išči</button>
      </div>
    </form>
  );
}
