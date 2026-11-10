// Slovenski nazivi statusov iz backenda in barva oznake (Bootstrap)
export const TOUR_STATUS = {
  DRAFT: { label: "Osnutek", color: "secondary" },
  CONFIRMED: { label: "Potrjena", color: "info" },
  IN_DELIVERY: { label: "V dostavi", color: "warning" },
  COMPLETED: { label: "Zaključena", color: "success" },
};

export const STOP_RESULT = {
  PENDING: { label: "Čaka", color: "secondary" },
  DELIVERED: { label: "Dostavljeno", color: "success" },
  NOT_DELIVERED: { label: "Ni dostavljeno", color: "danger" },
};
