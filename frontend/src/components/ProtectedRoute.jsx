import { Navigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth.js";
import ForbiddenPage from "../pages/ForbiddenPage.jsx";

// Stran prikaže samo prijavljenemu uporabniku z ustrezno vlogo
export default function ProtectedRoute({ role, children }) {
  const { user, loading } = useAuth();

  if (loading) return <p className="text-muted">Nalagam …</p>;
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <ForbiddenPage />;
  return children;
}
