// Barvna oznaka statusa, npr. <StatusBadge {...TOUR_STATUS[tour.status]} />
export default function StatusBadge({ label, color }) {
  // Pastelna oznaka: svetlo ozadje, temnejše besedilo in rob iste barve
  return (
    <span className={`badge bg-${color}-subtle text-${color}-emphasis border border-${color}-subtle`}>
      {label}
    </span>
  );
}
