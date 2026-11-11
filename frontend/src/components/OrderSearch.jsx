import { useState } from "react";
import { useNavigate } from "react-router-dom";

// Iskalno polje v glavi: ob potrditvi odpre stran z zadetki
export default function OrderSearch() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  function submit(event) {
    // Brskalnik bi ob oddaji obrazca stran naložil znova, zato to preprečimo
    event.preventDefault();
    if (query.trim()) navigate(`/orders/search?q=${encodeURIComponent(query.trim())}`);
  }

  return (
    <form className="d-flex gap-2" role="search" onSubmit={submit}>
      <input
        type="search"
        className="form-control form-control-sm"
        placeholder="Številka naročila ali stranka"
        aria-label="Iskanje naročila"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button className="btn btn-sm btn-outline-primary">Išči</button>
    </form>
  );
}
