import { createContext, useContext } from "react";

// Podatki o prijavljenem uporabniku, dostopni v vseh komponentah prek useAuth()
export const AuthContext = createContext(null);

export function useAuth() {
  return useContext(AuthContext);
}
