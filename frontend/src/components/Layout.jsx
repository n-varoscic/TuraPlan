import { Link, Outlet } from "react-router-dom";

// Skupna postavitev vseh strani: glava zgoraj, vsebina strani spodaj
export default function Layout() {
  return (
    <>
      <nav className="navbar navbar-dark bg-primary">
        <div className="container">
          <Link className="navbar-brand fw-bold" to="/">
            TuraPlan
          </Link>
        </div>
      </nav>
      <main className="container py-4">
        {/* Outlet je mesto, kamor React Router vstavi trenutno stran */}
        <Outlet />
      </main>
    </>
  );
}
