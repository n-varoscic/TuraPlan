import { useState } from "react";
import { pluralize } from "../format.js";

const MAX_LENGTH = 300;
const CHARACTERS = ["znak", "znaka", "znake", "znakov"];

// Opomba za voznika s števcem znakov, shrani se, ko polje izgubi fokus.
// Z gumbom jo disponent shrani kot stalno opombo stranke, ki se prikaže pri vseh njenih postankih
export default function DriverNoteInput({ stop, onSave, onSaveAsDeliveryNote }) {
  const [note, setNote] = useState(stop.driver_note);
  const tooLong = note.trim().length - MAX_LENGTH;

  function save() {
    if (note.trim() !== stop.driver_note && tooLong <= 0) onSave(note.trim());
  }

  return (
    <div className="mt-2">
      <div className="d-flex align-items-center gap-2">
        <input
          className={`form-control form-control-sm ${tooLong > 0 ? "is-invalid" : ""}`}
          value={note}
          onChange={(e) => setNote(e.target.value)}
          onBlur={save}
          onKeyDown={(e) => e.key === "Enter" && e.currentTarget.blur()}
          placeholder="Opomba za voznika"
          aria-label={`Opomba za voznika pri ${stop.order_number}`}
        />
        <span className={`small text-nowrap ${tooLong > 0 ? "text-danger-emphasis" : "text-muted"}`}>
          {note.trim().length}/{MAX_LENGTH}
        </span>
      </div>
      {note.trim() && tooLong <= 0 && note.trim() !== stop.delivery_note && (
        <button
          type="button"
          className="btn btn-link btn-sm p-0 small"
          // Brez tega bi polje ob kliku izgubilo fokus in se najprej shranilo kot opomba za voznika
          onMouseDown={(e) => e.preventDefault()}
          onClick={() => onSaveAsDeliveryNote(note.trim())}
        >
          📌 Shrani kot stalno opombo stranke
        </button>
      )}
      {tooLong > 0 && (
        <div className="small text-danger-emphasis mt-1">
          Opomba je predolga za {pluralize(tooLong, CHARACTERS)} in ni shranjena
        </div>
      )}
    </div>
  );
}
