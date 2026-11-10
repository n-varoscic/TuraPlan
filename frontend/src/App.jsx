import { Route, Routes } from "react-router-dom";
import { ROLES } from "./auth/roles.js";
import Layout from "./components/Layout.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import HomeRedirect from "./pages/HomeRedirect.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import MyToursPage from "./pages/MyToursPage.jsx";
import NotFoundPage from "./pages/NotFoundPage.jsx";
import TourDetailPage from "./pages/TourDetailPage.jsx";
import ToursPage from "./pages/ToursPage.jsx";

// Seznam strani: vsak naslov (path) prikaže svojo komponento
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<ProtectedRoute><HomeRedirect /></ProtectedRoute>} />
        <Route
          path="/tours"
          element={<ProtectedRoute role={ROLES.DISPATCHER}><ToursPage /></ProtectedRoute>}
        />
        <Route
          path="/tours/:id"
          element={<ProtectedRoute role={ROLES.DISPATCHER}><TourDetailPage /></ProtectedRoute>}
        />
        <Route
          path="/my-tours"
          element={<ProtectedRoute role={ROLES.DRIVER}><MyToursPage /></ProtectedRoute>}
        />
        <Route path="*" element={<ProtectedRoute><NotFoundPage /></ProtectedRoute>} />
      </Route>
    </Routes>
  );
}
