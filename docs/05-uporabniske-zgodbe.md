# 05 – Uporabniške zgodbe

## Pregled

| Oznaka | Funkcionalnost | Vloga | MVP |
|---|---|---|---|
| US-01 | F-01 Prijava in dostop glede na vlogo | vse vloge | **MVP** |
| US-02 | F-02 Seznam tur in napredek | Disponent | **MVP** |
| US-03 | F-03 Sestavljanje ture | Disponent | **MVP** |
| US-04 | F-04 Preverjanje kapacitete vozila | Disponent | **MVP** |
| US-05 | F-05 Razvrščanje postankov in opombe | Disponent | **MVP** |
| US-06 | F-06 Potrditev ture | Disponent | **MVP** |
| US-07 | F-07 Izvedba ture na telefonu | Voznik | **MVP** |
| US-08 | F-08 Iskanje naročila | Disponent | |
| US-09 | F-09 Nerazporejena naročila po regijah | Disponent |  |
| US-10 | F-10 Prikaz ture na zemljevidu | Disponent, Voznik |  |
| US-11 | F-11 Samodejna lokacija postanka na zemljevidu | Disponent |  |
| US-12 | F-12 Predlog vrstnega reda postankov | Disponent |  |
| US-13 | F-13 Izkoriščenost vozil | Disponent |  |
| US-14 | F-14 Upravljanje uporabniških dostopov | Administrator |  |
| US-15 | F-14 Evidenca vozil | Administrator |  |

---

## US-01 – Prijava in dostop glede na vlogo

- **Funkcionalnost:** F-01
- **Vloga:** Disponent, Voznik, Administrator

**Uporabniška zgodba:** Kot zaposleni (disponent, voznik ali administrator) želim prijavo z e-pošto in geslom, da vidim samo podatke in funkcije, ki jih potrebujem pri svojem delu, podatki o strankah in turah pa niso dostopni nepooblaščenim osebam.

**Sprejemni kriteriji:**

1. Po vnosu pravilne e-pošte in gesla je uporabnik prijavljen in preusmerjen na začetno stran svoje vloge (disponent: seznam tur, voznik: moje ture, administrator: administracija).
2. Ob napačni e-pošti ali geslu sistem prikaže sporočilo »Napačna e-pošta ali geslo«, ne da bi razkril, kateri od podatkov je napačen.
3. Neprijavljen uporabnik, ki odpre katero koli stran aplikacije, je preusmerjen na prijavno stran.
4. Uporabnik, ki odpre stran, ki ni namenjena njegovi vlogi, dobi sporočilo »Ni dostopa« (napaka 403).
5. Deaktiviran uporabnik se ne more prijaviti, tudi če vnese pravilno geslo.

---

## US-02 – Seznam tur in napredek dostav

- **Funkcionalnost:** F-02
- **Vloga:** Disponent

**Uporabniška zgodba:** Kot disponent želim na enem mestu videti vse ture z njihovim statusom, zasedenostjo vozil in napredkom dostav, da ahko po potrebi stranki sporočim informacije o predvidenem času dostave in hitro opazim morebitne težave.

**Sprejemni kriteriji:**

1. Seznam tur je privzeto razvrščen po datumu odpreme od današnjega dne naprej in ga je mogoče filtrirati po datumu odpreme in statusu.
2. Pri vsaki turi so prikazani datum odpreme, vozilo, voznik, število postankov, teža / nosilnost, palete / paletna mesta in status.
3. Pri turah v statusu `V_DOSTAVI` je prikazan napredek v obliki »7 / 12 dostavljeno, 1 nedostavljeno«.
4. Tura z vsaj enim nedostavljenim postankom je v seznamu označena z opozorilno oznako.
5. Ob kliku na turo disponent vidi vse postanke z rezultatom, časom označitve in razlogom nedostave.

---

## US-03 – Sestavljanje ture

- **Funkcionalnost:** F-03
- **Vloga:** Disponent

**Uporabniška zgodba:** Kot disponent želim ustvariti turo za izbrani datum odpreme in vanjo dodati nerazporejena naročila, da lahko dostave za vsako vozilo pripravim vnaprej, hitreje in nobeno naročilo ne ostane pozabljeno.

**Sprejemni kriteriji:**

1. Disponent lahko izbere samo aktivno vozilo in aktivnega voznika, ki na izbrani datum odpreme še nimata ture; zasedena vozila in vozniki v izbirnem seznamu niso na voljo.
2. Seznam naročil za dodajanje vsebuje samo naročila s statusom `NOVO` ali `NEDOSTAVLJENO`, je razvrščen po roku odpreme (najzgodnejši najprej) in ga je mogoče filtrirati po regiji stranke.
3. Naročila, katerih datum prejema je kasnejši od datuma odpreme ture, niso na voljo za dodajanje.
4. Če je datum odpreme ture kasnejši od roka odpreme naročila, je pri naročilu prikazano opozorilo »po roku odpreme«, dodajanje pa je dovoljeno.
5. Dodano naročilo dobi status `PLANIRANO` in izgine s seznama nerazporejenih naročil; ko ga disponent odstrani iz ture, se vrne v status `NOVO`.

---

## US-04 – Preverjanje kapacitete vozila

- **Funkcionalnost:** F-04
- **Vloga:** Disponent

**Uporabniška zgodba:** Kot disponent želim med sestavljanjem ture sproti videti, koliko teže in palet je že v turi glede na zmogljivost vozila, da vozila ne preobremenim in se izgonem, da bi bilo blago potrebno prelagati ob nakladanju.

**Sprejemni kriteriji:**

1. Na strani ture sta prikazani skupna teža naročil in nosilnost vozila (npr. `980 / 1.200 kg`) ter skupno število palet in paletnih mest (npr. `3,5 / 4`).
2. Prikazane vrednosti so posodobljene po vsakem dodajanju ali odstranjevanju naročila in po menjavi vozila.
3. Če skupna teža ali število palet presega zmogljivost vozila, je ta vrednost prikazana rdeče, pod njo pa opozorilo, za koliko je presežena (npr. »Preseženo za 1,5 palete«).
4. Vrednost, ki je točno enaka zmogljivosti (npr. `4 / 4` palete), ni označena kot presežena.
5. Turo s preseženo kapaciteto je mogoče shraniti kot osnutek, gumb za potrditev pa je onemogočen.

---

## US-05 – Razvrščanje postankov in opombe za voznika

- **Funkcionalnost:** F-05
- **Vloga:** Disponent

**Uporabniška zgodba:** Kot disponent želim določiti vrstni red postankov in vozniku pripisati opombe, da voznik ve, v kakšnem zaporedju naj dostavlja in na kaj mora biti pozoren pri posamezni stranki.

**Sprejemni kriteriji:**

1. Postanek je mogoče premakniti za eno mesto gor ali dol; zaporedne številke se po vsakem premiku preštevilčijo od 1 naprej brez lukenj in podvajanj.
2. Pri postanku je mogoče vnesti opombo za voznika z največ 300 znaki; daljše opombe sistem ne shrani in prikaže, za koliko znakov je predolga.
3. Stalna opomba stranke (npr. »zadnji vhod«) je samodejno prikazana pri vsakem postanku te stranke.
4. Ko disponent doda naročilo stranke, ki že ima postanek v turi, ga sistem samodejno uvrsti takoj za zadnji postanek te stranke.
5. Zaporedni postanki iste stranke so prikazani z enako barvo ozadja in oznako števila naročil (npr. »2 naročili«); če postanki iste stranke niso zaporedni, sistem prikaže opozorilo »postanki iste stranke niso zaporedni«.

---

## US-06 – Potrditev ture

- **Funkcionalnost:** F-06
- **Vloga:** Disponent

**Uporabniška zgodba:** Kot disponent želim turo potrditi in s tem zakleniti, da voznik dobi dokončen seznam dostav in se tura ne spremeni več po pomoti.

**Sprejemni kriteriji:**

1. Potrditev je mogoča samo, če ima tura vozilo, voznika, vsaj en postanek in kapaciteta ni presežena; sicer sistem prikaže seznam vseh neizpolnjenih pogojev.
2. Po potrditvi ima tura status `POTRJENA`, sistem zabeleži čas potrditve, tura pa postane vidna dodeljenemu vozniku.
3. Pri potrjeni turi ni mogoče dodajati ali odstranjevati naročil, spreminjati vrstnega reda postankov ali opomb.
4. Disponent lahko potrjeno turo vrne v `OSNUTEK`, dokler je voznik ni začel; pri turi v statusu `V_DOSTAVI` ta možnost ni na voljo.

---

## US-07 – Izvedba ture na telefonu

- **Funkcionalnost:** F-07
- **Vloga:** Voznik

**Uporabniška zgodba:** Kot voznik želim na telefonu videti svojo turo in pri vsakem postanku označiti, ali je bila dostava uspešna, da disponent sproti ve, kdaj in kaj je dostavljeno, in mi med vožnjo ni treba klicati v pisarno.

**Sprejemni kriteriji:**

1. Voznik vidi samo potrjene ture, v katerih je dodeljen kot voznik; ture drugih voznikov in ture v osnutku mu niso dostopne.
2. Postanki so prikazani po vrstnem redu s stranko, naslovom, telefonom, številko naročila, paletami, težo in opombami; stran je uporabna na zaslonu širine 360 px brez vodoravnega drsenja.
3. Gumb »Začni turo« je na voljo najprej na datum odpreme in samo, če voznik nima druge ture v statusu `V_DOSTAVI`.
4. Pri označitvi »Ni dostavljeno« je vnos razloga obvezen; naročilo dobi status `NEDOSTAVLJENO` in se pojavi med nerazporejenimi naročili disponenta.
5. Ko voznik označi zadnji postanek, tura samodejno preide v status `ZAKLJUCENA`.

---

## US-08 – Iskanje naročila

- **Funkcionalnost:** F-08
- **Vloga:** Disponent

**Uporabniška zgodba:** Kot disponent želim hitro poiskati naročilo po številki naročila ali nazivu stranke, da lahko stranki, ki pokliče, takoj povem, kje je njeno blago.

**Sprejemni kriteriji:**

1. Iskalno polje je dostopno na vseh straneh disponenta.
2. Iskanje po številki naročila vrne točno ujemanje; iskanje po nazivu stranke vrne delna ujemanja od 3 znakov naprej in ne razlikuje velikih in malih črk.
3. Pri vsakem zadetku so prikazani številka naročila, stranka, rok odpreme, status in – če je naročilo v turi – datum odpreme ture in voznik.
4. Pri nedostavljenem naročilu je prikazan razlog zadnje nedostave.
5. Če ni zadetkov, sistem prikaže sporočilo »Ni najdenih naročil«.

---

## US-09 – Nerazporejena naročila po regijah

- **Funkcionalnost:** F-09
- **Vloga:** Disponent

**Uporabniška zgodba:** Kot disponent želim videti nerazporejena naročila, združena po regijah, s seštevkom teže in palet, da hitro ocenim, koliko vozil potrebujem za posamezno regijo.

**Sprejemni kriteriji:**

1. Prikazana so samo naročila s statusom `NOVO` ali `NEDOSTAVLJENO`, združena po regiji stranke.
2. Za vsako regijo so prikazani število naročil, skupna teža (kg) in skupno število palet.
3. Naročila, katerih rok odpreme je pred današnjim dnem, so označena rdeče z oznako »zamuda«.
4. Nedostavljena naročila imajo oznako »nedostavljeno« in razlog zadnje nedostave.

---

## US-10 – Prikaz ture na zemljevidu

- **Funkcionalnost:** F-10
- **Vloga:** Disponent, Voznik

**Uporabniška zgodba:** Kot disponent želim turo videti na zemljevidu, da na prvi pogled preverim, ali je vrstni red postankov smiseln.

**Sprejemni kriteriji:**

1. Na strani ture je zemljevid z oznako za vsak postanek, oštevilčeno po zaporedju, in ločeno oznako skladišča.
2. Oznake so povezane s črto v vrstnem redu dostave, ki se začne pri skladišču.
3. Ob kliku na oznako se prikažejo naziv stranke, naslov in številka naročila.
4. Postanki strank brez koordinat niso na zemljevidu; pod zemljevidom je izpisano število in seznam postankov brez lokacije.
5. Enak zemljevid vidi tudi voznik v podrobnostih svoje ture.

---

## US-11 – Samodejna lokacija postanka na zemljevidu

- **Funkcionalnost:** F-11
- **Vloga:** Disponent

**Uporabniška zgodba:** Kot disponent želim, da se naročilo ob dodajanju v turo samodejno prikaže na zemljevidu na lokaciji stranke, da mi lokacije ni treba iskati ročno in takoj vidim, kam v turi postanek spada.

**Sprejemni kriteriji:**

1. Ko disponent doda naročilo v turo, sistem iz naslova, pošte in kraja stranke, na katero je vezano naročilo, določi koordinate, če jih stranka še nima.
2. Določene koordinate se shranijo pri stranki, zato se pri naslednjih naročilih iste stranke ne iščejo ponovno.
3. Postanek se takoj po dodajanju prikaže na zemljevidu ture z oznako svoje zaporedne številke.
4. Če lokacije ni mogoče določiti ali storitev ni dosegljiva, se naročilo vseeno doda v turo, pri postanku se prikaže opozorilo »Lokacija ni določena«, na zemljevidu pa postanek ni prikazan.
5. Če se naslov stranke v podatkih iz ERP sistema spremeni, sistem koordinate ob naslednjem dodajanju njenega naročila v turo določi ponovno.

---

## US-12 – Predlog vrstnega reda postankov

- **Funkcionalnost:** F-12
- **Vloga:** Disponent

**Uporabniška zgodba:** Kot disponent želim, da mi sistem predlaga vrstni red postankov, da prihranim čas pri planiranju.

**Sprejemni kriteriji:**

1. Predlog vrstnega reda je mogoče zahtevati samo pri turi v statusu `OSNUTEK`.
2. Predlog se začne pri skladišču in vsakič izbere najbližji še neobiskani postanek po zračni razdalji.
3. Postanki iste stranke v predlogu ostanejo zaporedni.
4. Postanki strank brez koordinat so postavljeni na konec, v obstoječem medsebojnem vrstnem redu.
5. Pred shranjevanjem disponent vidi predlagani vrstni red in skupno zračno razdaljo v km; predlog lahko sprejme ali zavrže, po sprejetju pa lahko postanke še ročno premika.

---

## US-13 – Pregled izkoriščenosti vozil

- **Funkcionalnost:** F-13
- **Vloga:** Disponent (dostop ima tudi Administrator)

**Uporabniška zgodba:** Kot disponent želim videti, kako polna so bila vozila po dnevih, da pri planiranju naslednjih tur bolje izkoristim vozila in po potrebi združim ture.

**Sprejemni kriteriji:**

1. Za izbrano obdobje (privzeto zadnjih 7 dni) je za vsako vozilo in vsak dan s turo prikazana izkoriščenost nosilnosti v % in paletnih mest v %.
2. Upoštevane so samo ture s statusom `POTRJENA`, `V_DOSTAVI` ali `ZAKLJUCENA`; osnutki niso upoštevani.
3. Izkoriščenost pod 50 % je posebej označena.
4. Za vsako vozilo je prikazana povprečna izkoriščenost v izbranem obdobju.
5. Pregled je dostopen disponentu in administratorju, vozniku ne.

---

## US-14 – Upravljanje uporabniških dostopov

- **Funkcionalnost:** F-14
- **Vloga:** Administrator

**Uporabniška zgodba:** Kot administrator želim dodajati uporabnike z ustrezno vlogo in jih deaktivirati, ko zapustijo podjetje, da imajo dostop do podatkov o strankah in turah samo zaposleni, ki ga pri svojem delu potrebujejo.

**Sprejemni kriteriji:**

1. Pri novem uporabniku sta obvezni e-pošta, ki še ne obstaja v sistemu, in vloga (`DISPONENT`, `VOZNIK` ali `ADMIN`).
2. Ko administrator uporabnika deaktivira (npr. ob odpovedi), se ta ne more več prijaviti, njegova obstoječa prijava pa preneha veljati ob naslednji zahtevi; njegove pretekle ture ostanejo nespremenjene.
3. Če ima deaktivirani voznik potrjene ture, ki se še niso začele, sistem administratorja na to opozori in jih navede, da jim disponent lahko dodeli drugega voznika.
4. Sprememba vloge začne veljati ob naslednji zahtevi uporabnika (npr. disponent, ki postane voznik, nima več dostopa do sestavljanja tur).
5. Administrator ne more deaktivirati sebe ali spremeniti svoje vloge.

---

## US-15 – Evidenca vozil

- **Funkcionalnost:** F-14
- **Vloga:** Administrator

**Uporabniška zgodba:** Kot administrator želim dodajati in urejati vozila z njihovo nosilnostjo in številom paletnih mest, da disponent pri planiranju izbira med dejansko razpoložljivimi vozili in sistem pravilno preverja njihovo kapaciteto.

**Sprejemni kriteriji:**

1. Pri vozilu so obvezni registrska številka, ki še ne obstaja v sistemu, tip (`KOMBI` ali `TOVORNJAK`), nosilnost, večja od 0 kg, in število paletnih mest, večje od 0.
2. Vozila, ki je že bilo v turi, ni mogoče izbrisati, mogoče ga je le deaktivirati.
3. Neaktivno vozilo ni na voljo pri izbiri vozila za novo turo; obstoječe ture s tem vozilom ostanejo nespremenjene.
4. Sprememba nosilnosti ali števila paletnih mest vpliva na preverjanje kapacitete samo pri turah v statusu `OSNUTEK`; potrjene ture se ne spremenijo.
5. Če ima deaktivirano vozilo potrjene ture, ki se še niso začele, sistem administratorja na to opozori in jih navede.
