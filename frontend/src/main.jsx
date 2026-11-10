import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
// Naša tema za Bootstrapom, da lahko prepiše njegove barve
import "./theme.css";
import App from "./App.jsx";
import AuthProvider from "./auth/AuthProvider.jsx";

// Vstopna točka: React aplikacijo izriše v <div id="root"> iz index.html
createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
);
