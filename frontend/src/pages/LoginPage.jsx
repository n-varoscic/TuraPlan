import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth.js";

export default function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Prijavljen uporabnik prijavne strani ne potrebuje
  if (user) return <Navigate to="/" replace />;

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
    }
  }

  return (
    <div className="row justify-content-center pt-md-5">
      <div className="col-12 col-sm-8 col-md-5 col-lg-4 card border shadow-sm p-4">
        <h1 className="h4 mb-3">Prijava</h1>
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label" htmlFor="email">E-pošta</label>
            <input
              id="email"
              type="email"
              className="form-control"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor="password">Geslo</label>
            <input
              id="password"
              type="password"
              className="form-control"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <div className="alert alert-danger py-2">{error}</div>}
          <button type="submit" className="btn btn-primary w-100" disabled={submitting}>
            {submitting ? "Prijavljam …" : "Prijava"}
          </button>
        </form>
      </div>
    </div>
  );
}
