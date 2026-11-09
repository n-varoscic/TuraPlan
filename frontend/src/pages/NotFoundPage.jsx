import { Link } from "react-router-dom";

// Prikaže se, ko naslov ne ustreza nobeni strani
export default function NotFoundPage() {
  return (
    <>
      <h1 className="h3">Stran ne obstaja</h1>
      <Link to="/">Nazaj na začetno stran</Link>
    </>
  );
}
