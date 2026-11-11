import { Link, Outlet } from "react-router-dom";
import { useAuth } from "../auth/useAuth.js";
import { ROLE_LABELS, ROLES } from "../auth/roles.js";
import OrderSearch from "./OrderSearch.jsx";

// Skupna postavitev vseh strani: glava zgoraj, vsebina strani spodaj
export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <>
      <nav className="navbar tp-navbar">
        <div className="container-fluid px-lg-4">
          <Link className="navbar-brand" to="/">
            TuraPlan
          </Link>
          {/* Iskanje naročil je na vseh straneh disponenta */}
          {user?.role === ROLES.DISPATCHER && <OrderSearch />}
          {user && (
            <div className="d-flex align-items-center gap-3">
              <span className="small">
                {user.first_name} {user.last_name} · {ROLE_LABELS[user.role]}
              </span>
              <button className="btn btn-sm btn-outline-primary" onClick={logout}>
                Odjava
              </button>
            </div>
          )}
        </div>
      </nav>
      {/* Vsebina seže čez celo širino okna, ob robu ostane le ozek odmik */}
      <main className="container-fluid px-lg-4 py-4">
        {/* Outlet je mesto, kamor React Router vstavi trenutno stran */}
        <Outlet />
      </main>
    </>
  );
}
