# OpenStreetMap za zemljevid in lokacije

## Kontekst in problem

- Funkcionalnosti izven MVP potrebujejo zemljevid in lokacije: prikaz ture na zemljevidu (F-10), lokacija postanka iz naslova stranke (F-11), predlog vrstnega reda postankov (F-12) ([02](../02-funkcionalnosti-in-obseg.md)).
- Jedro rešitve je planiranje tur in kontrola kapacitete, ne iskanje poti po cestah.
- Rešitev naj nima stroškov, plačilnega računa ali API ključev.
- MVP ne sme biti odvisen od zunanjih storitev.

## Obravnavane možnosti

- **OpenStreetMap (Leaflet + Nominatim)** – brezplačen odprt zemljevid; Leaflet ga prikaže na strani, Nominatim pretvori naslov v koordinate.
- **OpenStreetMap + openrouteservice** – isti zemljevid z dodatno brezplačno storitvijo za izračun poti po cestah; zahteva registracijo in API ključ.
- **Google Maps Platform** – zemljevid, iskanje naslovov in optimizacija poti po cestah; zahteva API ključ in plačilni račun, nad brezplačno kvoto je plačljiv.

## Odločitev

Izbrana možnost: **OpenStreetMap (Leaflet + Nominatim)**, ker:

- je brezplačen in ne potrebuje API ključa,
- zadošča za prikaz postankov in določanje lokacij,
- se predlog vrstnega reda izračuna z lastno preprosto metodo (najbližji naslednji postanek po zračni razdalji), zato storitev za poti po cestah v MVP ni potrebna.

### Posledice

- Dobro, ker ni stroškov in skrivnih ključev.
- Dobro, ker MVP deluje tudi, če zunanja storitev ni dosegljiva.
- Slabo, ker zračne razdalje niso dejanske ceste, zato predlog vrstnega reda ni vedno optimalen.
- Slabo, ker Nominatim omejuje število zahtev (približno ena na sekundo), zato se koordinate shranijo pri stranki.
- Slabo, ker bi pot po cestah zahtevala dodatno storitev (openrouteservice ali Google Maps) in nov ADR.
