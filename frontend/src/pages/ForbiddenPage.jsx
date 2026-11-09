import { Link } from "react-router-dom";

// Prikaže se, ko uporabnik odpre stran, ki ni namenjena njegovi vlogi (403)
export default function ForbiddenPage() {
  return (
    <>
      <h1 className="h3">Ni dostopa</h1>
      <p>Ta stran ni namenjena vaši vlogi.</p>
      <Link to="/">Na začetno stran</Link>
    </>
  );
}
