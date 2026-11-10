import { useEffect, useRef, useState } from "react";
import { formatDate, todayIso } from "../format.js";

const WEEKDAYS = ["po", "to", "sr", "če", "pe", "so", "ne"];

// Dnevi meseca kot "2026-11-10", pred prvim dnem prazna mesta, da se teden začne s ponedeljkom
function monthDays(year, month) {
  const blanks = Array((new Date(year, month, 1).getDay() + 6) % 7).fill(null);
  const count = new Date(year, month + 1, 0).getDate();
  const days = Array.from({ length: count }, (_, i) =>
    new Date(year, month, i + 1).toLocaleDateString("sv-SE"),
  );
  return [...blanks, ...days];
}

function monthTitle(year, month) {
  return new Date(year, month, 1).toLocaleDateString("sl-SI", { month: "long", year: "numeric" });
}

function rangeLabel(from, to) {
  if (from && from === to) return formatDate(from);
  if (from && to) return `${formatDate(from)} – ${formatDate(to)}`;
  if (from) return `od ${formatDate(from)} naprej`;
  if (to) return `do ${formatDate(to)}`;
  return "Vsi datumi";
}

// Izbira obdobja v koledarju: prvi klik izbere začetek (ali en dan), drugi klik konec
export default function DateRangePicker({ from, to, onChange }) {
  const [open, setOpen] = useState(false);
  const [selecting, setSelecting] = useState(false);
  const [hovered, setHovered] = useState("");
  const [view, setView] = useState(() => {
    const [year, month] = (from || todayIso()).split("-");
    return { year: Number(year), month: Number(month) - 1 };
  });
  const ref = useRef(null);

  // Klik izven koledarja ga zapre
  useEffect(() => {
    if (!open) return;
    function closeOnOutsideClick(event) {
      if (!ref.current.contains(event.target)) {
        setOpen(false);
        setSelecting(false);
      }
    }
    document.addEventListener("mousedown", closeOnOutsideClick);
    return () => document.removeEventListener("mousedown", closeOnOutsideClick);
  }, [open]);

  function pick(day) {
    // Konec ne sme biti pred začetkom: klik na zgodnejši dan začne novo izbiro
    if (selecting && day >= from) {
      onChange(from, day);
      setSelecting(false);
      setOpen(false);
    } else {
      onChange(day, day);
      setSelecting(true);
    }
  }

  function moveMonth(step) {
    setView(({ year, month }) => {
      const date = new Date(year, month + step, 1);
      return { year: date.getFullYear(), month: date.getMonth() };
    });
  }

  // Med izbiro konca obarvamo obdobje do dneva pod miško
  const end = selecting && hovered > from ? hovered : to;
  const today = todayIso();

  function dayClass(day) {
    let className = "tp-day";
    if (day === from || day === end) className += " tp-day-selected";
    else if (from && end && day > from && day < end) className += " tp-day-in-range";
    if (day === today) className += " tp-day-today";
    return className;
  }

  return (
    <div className="position-relative" ref={ref}>
      <button type="button" className="form-select text-start text-nowrap" style={{ minWidth: 240 }} onClick={() => setOpen(!open)}>
        {rangeLabel(from, to)}
      </button>
      {open && (
        <div className="tp-calendar card shadow p-3">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <button type="button" className="tp-day" onClick={() => moveMonth(-1)} aria-label="Prejšnji mesec">‹</button>
            <span className="fw-medium">{monthTitle(view.year, view.month)}</span>
            <button type="button" className="tp-day" onClick={() => moveMonth(1)} aria-label="Naslednji mesec">›</button>
          </div>
          <div className="tp-calendar-grid" onMouseLeave={() => setHovered("")}>
            {WEEKDAYS.map((weekday) => (
              <div key={weekday} className="small text-muted text-center">{weekday}</div>
            ))}
            {monthDays(view.year, view.month).map((day, index) =>
              day ? (
                <button
                  key={day}
                  type="button"
                  className={dayClass(day)}
                  onClick={() => pick(day)}
                  onMouseEnter={() => setHovered(day)}
                >
                  {Number(day.slice(8))}
                </button>
              ) : (
                <span key={`blank-${index}`} />
              ),
            )}
          </div>
          <p className="small text-muted mb-0 mt-2">
            {selecting ? "Izberi končni datum ali klikni drugam za en dan" : "Izberi začetni datum"}
          </p>
        </div>
      )}
    </div>
  );
}
