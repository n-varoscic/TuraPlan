// Napredek dostav ture, prikazan samo med dostavo in po zaključku
export default function DeliveryProgress({ tour }) {
  const started = tour.status === "IN_DELIVERY" || tour.status === "COMPLETED";
  const percent = (count) => `${tour.stop_count ? (count / tour.stop_count) * 100 : 0}%`;

  return (
    <div className="d-flex align-items-center gap-2">
      {started ? (
        <>
          {/* Zeleni del so dostavljeni, rdeči nedostavljeni postanki */}
          <div className="progress-stacked flex-grow-1" style={{ minWidth: 80, maxWidth: 140 }}>
            <div className="progress" style={{ width: percent(tour.delivered_count) }}>
              <div className="progress-bar bg-success" />
            </div>
            <div className="progress" style={{ width: percent(tour.not_delivered_count) }}>
              <div className="progress-bar bg-danger" />
            </div>
          </div>
          <span className="small text-nowrap">
            {tour.delivered_count} / {tour.stop_count} dostavljeno
            {tour.not_delivered_count > 0 && `, ${tour.not_delivered_count} nedostavljeno`}
          </span>
        </>
      ) : (
        <span className="text-muted">–</span>
      )}
      {/* Opozorilo, če vsaj en postanek ni bil dostavljen */}
      {tour.not_delivered_count > 0 && (
        <span className="text-danger" title="Tura ima nedostavljene postanke">
          ⚠
        </span>
      )}
    </div>
  );
}
