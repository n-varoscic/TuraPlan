import { useEffect } from "react";
import { Navigate } from "react-router-dom";
import { ADMIN_URL } from "../api/client.js";
import { useAuth } from "../auth/useAuth.js";
import { ROLE_HOME, ROLES } from "../auth/roles.js";

// Na naslovu "/" uporabnika preusmeri na začetno stran njegove vloge
export default function HomeRedirect() {
  const { user } = useAuth();
  const isAdmin = user.role === ROLES.ADMIN;

  // Administrator dela v Django Adminu, ki je del backenda
  useEffect(() => {
    if (isAdmin) window.location.replace(ADMIN_URL);
  }, [isAdmin]);

  if (isAdmin) return <p className="text-muted">Preusmerjam v administracijo …</p>;
  return <Navigate to={ROLE_HOME[user.role]} replace />;
}
