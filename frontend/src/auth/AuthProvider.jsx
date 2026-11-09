import { useEffect, useState } from "react";
import * as api from "../api/client.js";
import { AuthContext } from "./useAuth.js";

// Hrani prijavljenega uporabnika in ga ponudi vsem komponentam znotraj sebe
export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // Če je žeton shranjen, najprej preverimo, komu pripada
  const [loading, setLoading] = useState(api.hasToken());

  useEffect(() => {
    if (!api.hasToken()) return;
    api
      .getMe()
      .then(setUser)
      .catch(() => api.logout())
      .finally(() => setLoading(false));
  }, []);

  async function login(email, password) {
    await api.login(email, password);
    const me = await api.getMe();
    setUser(me);
    return me;
  }

  function logout() {
    api.logout();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
