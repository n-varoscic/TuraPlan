// Vloge uporabnikov (enake vrednosti kot v backendu) in njihovi nazivi
export const ROLES = {
  DISPATCHER: "DISPATCHER",
  DRIVER: "DRIVER",
  ADMIN: "ADMIN",
};

export const ROLE_LABELS = {
  DISPATCHER: "Disponent",
  DRIVER: "Voznik",
  ADMIN: "Administrator",
};

// Začetna stran posamezne vloge po prijavi
export const ROLE_HOME = {
  DISPATCHER: "/tours",
  DRIVER: "/my-tours",
};
