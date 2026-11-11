from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from tours.models import Customer, Order, Settings, Stop, Tour, Vehicle
from tours.services import customer_address
from users.models import User

# Geslo vseh testnih uporabnikov (samo za lokalni razvoj)
SEED_PASSWORD = "turaplan123"

# Uporabniki s stalno vlogo v testnih podatkih, na te e-pošte se sklicujejo tudi testi
DISPATCHER_EMAIL = "dejan.zupan@turaplan.si"
# Danes ima turo v dostavi, jutri osnutek
DRIVER_VID_EMAIL = "vid.krajnc@turaplan.si"
# Včeraj je zaključila turo
DRIVER_MAJA_EMAIL = "maja.kovac@turaplan.si"
# Jutri ima potrjeno turo
DRIVER_LUKA_EMAIL = "luka.horvat@turaplan.si"

USERS = [
    # e-pošta, ime, priimek, vloga
    ("ana.novak@turaplan.si", "Ana", "Novak", User.Role.ADMIN),
    (DISPATCHER_EMAIL, "Dejan", "Zupan", User.Role.DISPATCHER),
    (DRIVER_VID_EMAIL, "Vid", "Krajnc", User.Role.DRIVER),
    (DRIVER_MAJA_EMAIL, "Maja", "Kovač", User.Role.DRIVER),
    (DRIVER_LUKA_EMAIL, "Luka", "Horvat", User.Role.DRIVER),
    ("nejc.potocnik@turaplan.si", "Nejc", "Potočnik", User.Role.DRIVER),
    ("zan.kovacic@turaplan.si", "Žan", "Kovačič", User.Role.DRIVER),
    ("tilen.vidmar@turaplan.si", "Tilen", "Vidmar", User.Role.DRIVER),
    ("anze.oblak@turaplan.si", "Anže", "Oblak", User.Role.DRIVER),
    ("blaz.zupancic@turaplan.si", "Blaž", "Zupančič", User.Role.DRIVER),
    ("eva.hribar@turaplan.si", "Eva", "Hribar", User.Role.DRIVER),
    ("david.rupnik@turaplan.si", "David", "Rupnik", User.Role.DRIVER),
    ("jan.bizjak@turaplan.si", "Jan", "Bizjak", User.Role.DRIVER),
    ("matic.kolar@turaplan.si", "Matic", "Kolar", User.Role.DRIVER),
    ("sara.petric@turaplan.si", "Sara", "Petrič", User.Role.DRIVER),
    ("klemen.erjavec@turaplan.si", "Klemen", "Erjavec", User.Role.DRIVER),
    ("primoz.znidarsic@turaplan.si", "Primož", "Žnidaršič", User.Role.DRIVER),
]

# Testni uporabniki iz prejšnje različice podatkov, ki jih ob ponastavitvi odstranimo
OLD_EMAILS = [
    "admin@turaplan.si", "disponent@turaplan.si", "voznik@turaplan.si", "voznik2@turaplan.si",
    "voznik3@turaplan.si",
]

VEHICLES = [
    # registrska, tip, nosilnost, paletna mesta, aktivno
    ("MB AB-123", Vehicle.Type.VAN, 1200, 4, True),
    ("MB CD-456", Vehicle.Type.VAN, 1200, 4, True),
    ("MB EF-217", Vehicle.Type.VAN, 1200, 4, True),
    ("MB GH-548", Vehicle.Type.VAN, 1200, 4, True),
    ("MB KL-306", Vehicle.Type.VAN, 1200, 4, True),
    ("MB MN-871", Vehicle.Type.VAN, 1200, 4, True),
    # Neaktivno vozilo se pri novi turi ne ponuja
    ("MB PR-632", Vehicle.Type.VAN, 1200, 4, False),
    ("MB TR-789", Vehicle.Type.TRUCK, 8000, 16, True),
    ("MB TV-145", Vehicle.Type.TRUCK, 8000, 16, True),
    ("MB UZ-902", Vehicle.Type.TRUCK, 8000, 16, True),
    ("MB VA-357", Vehicle.Type.TRUCK, 9000, 17, True),
    ("MB VC-680", Vehicle.Type.TRUCK, 9000, 17, True),
    ("MB ZD-214", Vehicle.Type.TRUCK, 9000, 17, True),
    ("MB JK-449", Vehicle.Type.TRUCK, 9000, 17, True),
    ("MB ZE-593", Vehicle.Type.TRUCK, 10000, 18, True),
    ("MB BF-760", Vehicle.Type.TRUCK, 10000, 18, True),
    ("MB DH-128", Vehicle.Type.TRUCK, 10000, 18, True),
]

# Skladišče v Mariboru, od tod se začne vsaka tura
WAREHOUSE = ("Tržaška cesta 65, 2000 Maribor", "46.523286", "15.650472")

# Imena strank so izmišljena, naslovi so resnični, koordinate so poiskane vnaprej pri Nominatimu
CUSTOMERS = [
    # šifra, naziv, naslov, pošta, kraj, regija, širina, dolžina, kontaktna oseba, telefon, stalna opomba
    ("C001", "Pekarna Zrno", "Glavni trg 5", "2000", "Maribor", "Podravska", "46.557295", "15.645025", "Petra Kotnik", "02 724 92 23", "Zadnji vhod, zvoniti 2x"),
    ("C002", "Slaščičarna Mak", "Partizanska cesta 12", "2000", "Maribor", "Podravska", "46.560232", "15.651961", "Mojca Medved", "02 630 83 80", ""),
    ("C003", "Pekarna Klas", "Ormoška cesta 30", "2250", "Ptuj", "Podravska", "46.415902", "15.883923", "Polona Žagar", "02 800 66 40", ""),
    ("C004", "Kavarna Drava", "Slovenski trg 3", "2250", "Ptuj", "Podravska", "46.419820", "15.869867", "Marko Medved", "041 300 560", ""),
    ("C005", "Gostilna Stari hrast", "Ljubljanska cesta 42", "2310", "Slovenska Bistrica", "Podravska", "46.388704", "15.569257", "Marko Lah", "02 521 36 60", ""),
    ("C006", "Okrepčevalnica Klopca", "Trg osvoboditve 7", "2230", "Lenart v Slovenskih goricah", "Podravska", "46.576039", "15.830653", "Tomaž Kavčič", "02 565 58 75", ""),
    ("C007", "Pekarna Rženi hlebec", "Falska cesta 24", "2342", "Ruše", "Podravska", "46.538792", "15.510216", "Miha Kos", "02 291 81 78", ""),
    ("C008", "Gostilna Pod Pohorjem", "Pohorska cesta 15", "2311", "Hoče", "Podravska", "46.498546", "15.646876", "Katja Hribar", "02 860 83 49", ""),
    ("C009", "Restavracija Zlati grič", "Ptujska cesta 20", "2327", "Rače", "Podravska", "46.449475", "15.682532", "Marko Jerman", "02 672 64 21", "Rampa na dvorišču"),
    ("C010", "Slaščičarna Rožica", "Ptujska cesta 12", "2270", "Ormož", "Podravska", "46.407472", "16.145323", "Gregor Zajc", "02 319 64 74", ""),
    ("C011", "Okrepčevalnica Pri mostu", "Starše 20", "2205", "Starše", "Podravska", "46.469702", "15.769699", "Tanja Žagar", "02 737 43 63", ""),
    ("C012", "Kavarna Štorklja", "Kocljeva ulica 6", "9000", "Murska Sobota", "Pomurska", "46.660124", "16.163211", "Rok Žagar", "02 225 83 38", ""),
    ("C013", "Restavracija Ravnica", "Lendavska ulica 20", "9000", "Murska Sobota", "Pomurska", "46.664110", "16.168336", "Matej Golob", "02 735 95 23", ""),
    ("C014", "Slaščičarna Gibanica", "Glavna ulica 30", "9220", "Lendava", "Pomurska", "46.553960", "16.438976", "Jure Medved", "02 345 71 39", ""),
    ("C015", "Gostilna Pri brodu", "Mladinska ulica 4", "9231", "Beltinci", "Pomurska", "46.606326", "16.235781", "Petra Pirc", "02 890 70 79", ""),
    ("C016", "Kavarna Vrelec", "Radgonska cesta 10", "9252", "Radenci", "Pomurska", "46.642859", "16.038304", "Tomaž Koren", "02 515 80 92", ""),
    ("C017", "Kmečki turizem Bučnica", "Kranjčeva ulica 20", "9226", "Moravske Toplice", "Pomurska", "46.685437", "16.220550", "Simon Jerman", "02 611 65 35", ""),
    ("C018", "Okrepčevalnica Jelša", "Ulica Štefana Kovača 10", "9224", "Turnišče", "Pomurska", "46.616928", "16.320784", "Katja Bizjak", "040 871 711", ""),
    ("C019", "Gostilna Goričko", "Puconci 80", "9201", "Puconci", "Pomurska", "46.704644", "16.153932", "Aleš Hočevar", "02 568 35 43", ""),
    ("C020", "Slaščičarna Ajda", "Cankova 20", "9261", "Cankova", "Pomurska", "46.716635", "16.019806", "Jure Žagar", "02 709 65 81", ""),
    ("C021", "Kavarna Ravensko", "Dobrovnik 100", "9223", "Dobrovnik", "Pomurska", "46.648516", "16.348853", "Sabina Golob", "02 524 68 22", ""),
    ("C022", "Okrepčevalnica Bograč", "Tešanovci 20", "9226", "Moravske Toplice", "Pomurska", "46.681245", "16.242265", "Aleš Jerman", "02 727 43 67", ""),
    ("C023", "Gostilna Lipa", "Mariborska cesta 8", "3000", "Celje", "Savinjska", "46.233276", "15.268864", "Nina Petek", "03 690 18 93", "Dostava skozi kuhinjo"),
    ("C024", "Kavarna Sonce", "Ljubljanska cesta 50", "3000", "Celje", "Savinjska", "46.235718", "15.246010", "Tomaž Žagar", "03 399 62 28", ""),
    ("C025", "Restavracija Jezero", "Šaleška cesta 20", "3320", "Velenje", "Savinjska", "46.359264", "15.117956", "Aleš Vidmar", "051 794 659", ""),
    ("C026", "Slaščičarna Hmelj", "Šlandrov trg 10", "3310", "Žalec", "Savinjska", "46.251372", "15.168666", "Andrej Medved", "03 453 25 89", ""),
    ("C027", "Gostilna Pri kovaču", "Ulica Dušana Kvedra 10", "3230", "Šentjur", "Savinjska", "46.216900", "15.394735", "Tina Koren", "03 884 91 55", ""),
    ("C028", "Okrepčevalnica Smreka", "Na trgu 10", "3330", "Mozirje", "Savinjska", "46.339140", "14.961615", "Matej Vidmar", "03 797 83 72", ""),
    ("C029", "Restavracija Kristal", "Celjska cesta 10", "3250", "Rogaška Slatina", "Savinjska", "46.239120", "15.634339", "Jure Kokalj", "03 758 38 70", ""),
    ("C030", "Gostilna Hmeljar", "Braslovče 20", "3314", "Braslovče", "Savinjska", "46.287177", "15.040627", "Rok Kralj", "03 716 47 20", ""),
    ("C031", "Pekarna Hlebec", "Celjska cesta 20", "3212", "Vojnik", "Savinjska", "46.292247", "15.301820", "Urška Lah", "040 800 413", ""),
    ("C032", "Kmečki turizem Zeleni breg", "Vransko 30", "3305", "Vransko", "Savinjska", "46.244002", "14.949652", "Simon Petek", "03 352 76 35", ""),
    ("C033", "Gostilna Ob Savinji", "Rečica ob Savinji 30", "3332", "Rečica ob Savinji", "Savinjska", "46.326166", "14.924231", "Gregor Vidmar", "03 598 19 16", ""),
    ("C034", "Slaščičarna Medenjak", "Dobrna 10", "3204", "Dobrna", "Savinjska", "46.335022", "15.224760", "Špela Pirc", "03 226 13 75", ""),
    ("C035", "Gostilna Pri Paki", "Šmartno ob Paki 20", "3327", "Šmartno ob Paki", "Savinjska", "46.327540", "15.035364", "Barbara Kotnik", "03 660 51 25", ""),
    ("C036", "Gostilna Termalni vrelec", "Malteška cesta 20", "3313", "Polzela", "Savinjska", "46.278765", "15.080206", "Barbara Kolar", "03 374 29 85", ""),
    ("C037", "Pekarna Pri mlinu", "Celovška cesta 111", "1000", "Ljubljana", "Osrednjeslovenska", "46.068551", "14.490352", "Simon Božič", "01 544 68 86", "Dostava do 7.00"),
    ("C038", "Kavarna Center", "Slovenska cesta 27", "1000", "Ljubljana", "Osrednjeslovenska", "46.051216", "14.502657", "Mojca Lah", "01 760 61 14", ""),
    ("C039", "Restavracija Barje", "Tržaška cesta 132", "1000", "Ljubljana", "Osrednjeslovenska", "46.038271", "14.467802", "Janez Pirc", "01 246 92 79", ""),
    ("C040", "Pekarna Slamnik", "Ljubljanska cesta 80", "1230", "Domžale", "Osrednjeslovenska", "46.140479", "14.593548", "Tina Kolar", "01 856 34 71", ""),
    ("C041", "Gostilna Planinka", "Glavni trg 10", "1241", "Kamnik", "Osrednjeslovenska", "46.225433", "14.611363", "Jure Lah", "01 332 92 77", ""),
    ("C042", "Okrepčevalnica Močvirnik", "Tržaška cesta 10", "1360", "Vrhnika", "Osrednjeslovenska", "45.963893", "14.296407", "Janez Hočevar", "01 341 30 94", ""),
    ("C043", "Pekarna Sora", "Zgornje Pirniče 20", "1215", "Medvode", "Osrednjeslovenska", "46.139223", "14.431714", "Nina Rozman", "051 280 492", ""),
    ("C044", "Kmečki turizem Krim", "Podpeč 20", "1352", "Preserje", "Osrednjeslovenska", "45.968866", "14.415548", "Katja Turk", "01 469 69 73", ""),
    ("C045", "Slaščičarna Jagoda", "Šmarska cesta 10", "1291", "Škofljica", "Osrednjeslovenska", "45.984671", "14.578694", "Urška Hribar", "01 533 76 71", ""),
    ("C046", "Gostilna Črni graben", "Stari trg 1", "1225", "Lukovica", "Osrednjeslovenska", "46.169530", "14.692026", "Aleš Mlakar", "01 737 45 22", ""),
    ("C047", "Kavarna Ižanka", "Banija 4", "1292", "Ig", "Osrednjeslovenska", "45.958983", "14.527179", "Janez Korošec", "031 665 761", ""),
    ("C048", "Pekarna Jezerska", "Ljubljanska cesta 4", "4260", "Bled", "Gorenjska", "46.366627", "14.109065", "Boštjan Petek", "04 886 33 13", ""),
    ("C049", "Kavarna Storžič", "Koroška cesta 10", "4000", "Kranj", "Gorenjska", "46.243642", "14.354931", "Špela Turk", "04 786 78 37", ""),
    ("C050", "Restavracija Stara pošta", "Glavni trg 10", "4000", "Kranj", "Gorenjska", "46.238280", "14.355183", "Petra Medved", "04 769 82 37", ""),
    ("C051", "Slaščičarna Planika", "Cesta maršala Tita 20", "4270", "Jesenice", "Gorenjska", "46.436763", "14.055986", "Rok Hribar", "04 886 81 26", ""),
    ("C052", "Gostilna Loški hrib", "Kidričeva cesta 10", "4220", "Škofja Loka", "Gorenjska", "46.167213", "14.314304", "Petra Bizjak", "051 375 208", ""),
    ("C053", "Gostilna Pod Špikom", "Borovška cesta 50", "4280", "Kranjska Gora", "Gorenjska", "46.485951", "13.788801", "Sabina Golob", "04 389 92 90", ""),
    ("C054", "Kmečki turizem Bohinjka", "Srednja vas v Bohinju 50", "4267", "Srednja vas v Bohinju", "Gorenjska", "46.297749", "13.926413", "Petra Hočevar", "04 802 18 47", "Poklicati 15 minut prej"),
    ("C055", "Slaščičarna Čebelica", "Breznica 3", "4274", "Žirovnica", "Gorenjska", "46.395863", "14.152458", "Boštjan Turk", "031 214 521", ""),
    ("C056", "Gostilna Pri Radovni", "Zgornje Gorje 20", "4247", "Zgornje Gorje", "Gorenjska", "46.378913", "14.068099", "Tomaž Petek", "04 258 22 40", ""),
    ("C057", "Kavarna Draga", "Begunje na Gorenjskem 20", "4275", "Begunje na Gorenjskem", "Gorenjska", "46.374169", "14.199659", "Marko Hribar", "041 522 898", ""),
    ("C058", "Okrepčevalnica Ob Savi", "Podnart 20", "4244", "Podnart", "Gorenjska", "46.291627", "14.259914", "Aleš Medved", "04 829 14 61", ""),
    ("C059", "Pekarna Soča", "Delpinova ulica 10", "5000", "Nova Gorica", "Goriška", "45.954493", "13.645348", "Boštjan Medved", "051 636 792", ""),
    ("C060", "Kavarna Burja", "Goriška cesta 20", "5270", "Ajdovščina", "Goriška", "45.887381", "13.904298", "Petra Lah", "05 713 97 42", ""),
    ("C061", "Slaščičarna Čipka", "Mestni trg 5", "5280", "Idrija", "Goriška", "46.001175", "14.021972", "Gregor Hribar", "05 564 17 65", ""),
    ("C062", "Kmečki turizem Vipavska klet", "Glavni trg 5", "5271", "Vipava", "Goriška", "45.845869", "13.962602", "Marko Hribar", "05 496 25 48", ""),
    ("C063", "Okrepčevalnica Rožna dolina", "Cesta Prekomorskih brigad 20", "5290", "Šempeter pri Gorici", "Goriška", "45.931111", "13.639358", "Urška Kotnik", "05 220 79 53", ""),
    ("C064", "Kavarna Kanin", "Trg golobarskih žrtev 10", "5230", "Bovec", "Goriška", "46.338216", "13.551482", "Janez Koren", "031 366 733", ""),
    ("C065", "Pekarna Kanalka", "Trg svobode 10", "5213", "Kanal", "Goriška", "46.085270", "13.633170", "Petra Mlakar", "041 811 763", ""),
    ("C066", "Gostilna Brda", "Kojsko 20", "5211", "Kojsko", "Goriška", "46.006729", "13.575727", "Miha Hribar", "040 564 525", ""),
    ("C067", "Gostilna Pod Čavnom", "Črniče 20", "5262", "Črniče", "Goriška", "45.907334", "13.780075", "Gregor Rozman", "051 878 324", ""),
    ("C068", "Restavracija Most", "Most na Soči 50", "5216", "Most na Soči", "Goriška", "46.152906", "13.741818", "Matej Turk", "05 877 79 97", ""),
    ("C069", "Gostilna Pri vodnjaku", "Šempas 50", "5261", "Šempas", "Goriška", "45.928756", "13.748328", "Irena Rozman", "05 351 39 12", ""),
    ("C070", "Pekarna Gorjanci", "Glavni trg 10", "8000", "Novo mesto", "Dolenjska", "45.803424", "15.170390", "Marko Bizjak", "07 627 43 50", ""),
    ("C071", "Kavarna Breg", "Seidlova cesta 10", "8000", "Novo mesto", "Dolenjska", "45.809290", "15.164914", "Matej Pirc", "07 383 80 14", ""),
    ("C072", "Restavracija Trška gora", "Šmarješka cesta 20", "8000", "Novo mesto", "Dolenjska", "45.819794", "15.182047", "Miha Hočevar", "07 548 91 76", ""),
    ("C073", "Gostilna Cviček", "Gubčeva cesta 10", "8210", "Trebnje", "Dolenjska", "45.907861", "15.009376", "Polona Kotnik", "031 842 348", ""),
    ("C074", "Slaščičarna Bela krajina", "Kolodvorska cesta 10", "8340", "Črnomelj", "Dolenjska", "45.572223", "15.192786", "Barbara Golob", "07 895 75 29", ""),
    ("C075", "Pekarna Rog", "Ljubljanska cesta 10", "1330", "Kočevje", "Dolenjska", "45.640958", "14.858457", "Polona Rozman", "07 568 39 81", ""),
    ("C076", "Pekarna Temenica", "Trg 10", "8216", "Mirna Peč", "Dolenjska", "45.857954", "15.087371", "Tomaž Kotnik", "07 583 55 68", ""),
    ("C077", "Gostilna Pri Krki", "Ulica talcev 10", "8351", "Straža", "Dolenjska", "45.782793", "15.072728", "Miha Kolar", "07 685 96 84", ""),
    ("C078", "Kavarna Težka voda", "Stopiče 20", "8322", "Stopiče", "Dolenjska", "45.769160", "15.206780", "Katja Božič", "051 357 596", ""),
    ("C079", "Gostilna Pod Gorjanci", "Velike Brusnice 50", "8321", "Brusnice", "Dolenjska", "45.808538", "15.258930", "Marko Kavčič", "07 735 62 14", ""),
    ("C080", "Okrepčevalnica Luknja", "Prečna 20", "8000", "Novo mesto", "Dolenjska", "45.815019", "15.119297", "Miha Turk", "041 759 848", ""),
    ("C081", "Pekarna Burin", "Pristaniška ulica 10", "6000", "Koper", "Obalno-kraška", "45.544209", "13.729161", "Tomaž Kralj", "05 303 12 78", "Rampa 2"),
    ("C082", "Restavracija Sidro", "Cankarjev drevored 10", "6310", "Izola", "Obalno-kraška", "45.536954", "13.661701", "Janez Jerman", "05 786 15 60", ""),
    ("C083", "Slaščičarna Školjka", "Obala 20", "6320", "Portorož", "Obalno-kraška", "45.512483", "13.594861", "Gregor Koren", "05 728 92 94", ""),
    ("C084", "Kmečki turizem Teran", "Partizanska cesta 20", "6210", "Sežana", "Obalno-kraška", "45.708690", "13.872132", "Nina Hočevar", "040 950 498", ""),
    ("C085", "Okrepčevalnica Oljka", "Jadranska cesta 20", "6280", "Ankaran", "Obalno-kraška", "45.577045", "13.745179", "Boštjan Koren", "031 955 706", ""),
    ("C086", "Gostilna Kraški rob", "Kraška cesta 20", "6215", "Divača", "Obalno-kraška", "45.684666", "13.971871", "Sabina Božič", "041 502 654", ""),
    ("C087", "Gostilna Istrska hiša", "Dekani 100", "6271", "Dekani", "Obalno-kraška", "45.546303", "13.814035", "Katja Kavčič", "051 393 864", ""),
    ("C088", "Okrepčevalnica Pri meji", "Spodnje Škofije 100", "6281", "Škofije", "Obalno-kraška", "45.571218", "13.791603", "Miha Vidmar", "05 863 71 64", ""),
    ("C089", "Gostilna Refošk", "Marezige 20", "6273", "Marezige", "Obalno-kraška", "45.505561", "13.795397", "Špela Koren", "031 383 422", ""),
    ("C090", "Restavracija Kraška jama", "Lokev 100", "6219", "Lokev", "Obalno-kraška", "45.661711", "13.927327", "Irena Kralj", "031 727 783", ""),
    ("C091", "Pekarna Istrska", "Šmarje 50", "6274", "Šmarje", "Obalno-kraška", "45.499626", "13.717237", "Jure Pirc", "05 583 18 57", ""),
]

ORDERS = [
    # številka, šifra stranke, prejeto (dni od danes), rok odpreme (dni od danes), teža kg, palete, opis
    ("N-001", "C020", -4, -1, "200", "0.5", "embalaža"),  # Slaščičarna Ajda
    ("N-002", "C012", -4, -1, "180", "0.5", "nadevi"),  # Kavarna Štorklja
    ("N-003", "C022", -4, -1, "220", "0.75", "čokolada, oreščki"),  # Okrepčevalnica Bograč
    ("N-004", "C021", -4, -1, "150", "0.5", "kvas, sol"),  # Kavarna Ravensko
    ("N-005", "C018", -4, -1, "170", "0.5", "moka, semena"),  # Okrepčevalnica Jelša
    ("N-006", "C001", -3, 0, "180", "0.5", "nadevi"),  # Pekarna Zrno
    ("N-007", "C002", -3, 0, "150", "0.5", "kvas, sol"),  # Slaščičarna Mak
    ("N-008", "C007", -3, 0, "220", "0.75", "kava, sladkor"),  # Pekarna Rženi hlebec
    ("N-009", "C006", -3, 0, "140", "0.5", "podstavki, vrečke"),  # Okrepčevalnica Klopca
    ("N-010", "C011", -3, 0, "160", "0.5", "mleko, smetana"),  # Okrepčevalnica Pri mostu
    ("N-011", "C070", -1, 1, "180", "0.5", "moka T-500 6 vreč"),  # Pekarna Gorjanci
    ("N-012", "C070", -1, 2, "150", "0.5", "embalaža"),  # Pekarna Gorjanci
    ("N-013", "C002", -5, -2, "150", "0.5", "kava, sladkor"),  # Slaščičarna Mak
    ("N-014", "C003", -1, 1, "600", "1.5", "moka, semena, kvas"),  # Pekarna Klas
    ("N-015", "C004", -1, 2, "250", "0.75", "embalaža"),  # Kavarna Drava
    ("N-016", "C005", -1, 2, "700", "1.5", "olje, moka, sol"),  # Gostilna Stari hrast
    ("N-017", "C013", -1, 2, "700", "1.25", "nadevi, embalaža"),  # Restavracija Ravnica
    ("N-018", "C015", -2, 1, "540", "1", "sir 40 kg, mleko"),  # Gostilna Pri brodu
    ("N-019", "C008", 0, 3, "550", "1.25", "sir 40 kg, mleko"),  # Gostilna Pod Pohorjem
    ("N-020", "C016", 0, 2, "200", "0.5", "moka, semena"),  # Kavarna Vrelec
    ("N-021", "C009", -1, 4, "1800", "5.5", "moka, sladkor, kvas"),  # Restavracija Zlati grič
    ("N-022", "C017", -1, 1, "540", "1", "moka T-400 25 vreč"),  # Kmečki turizem Bučnica
    ("N-023", "C001", 0, 4, "250", "0.75", "podstavki, vrečke"),  # Pekarna Zrno
    ("N-024", "C003", 0, 5, "500", "1.25", "nadevi, embalaža"),  # Pekarna Klas
    ("N-025", "C038", 0, 5, "120", "0.25", "čokolada, oreščki"),  # Kavarna Center
    ("N-026", "C014", -4, -1, "190", "0.75", "moka, semena"),  # Slaščičarna Gibanica
    ("N-027", "C004", -3, 0, "130", "0.5", "kava, sladkor"),  # Kavarna Drava
    ("N-028", "C010", -3, 0, "120", "0.5", "kava, sladkor"),  # Slaščičarna Rožica
    ("N-029", "C071", -2, 1, "120", "0.25", "moka, semena"),  # Kavarna Breg
    ("N-030", "C080", -2, 1, "200", "0.75", "embalaža"),  # Okrepčevalnica Luknja
    ("N-031", "C077", -2, 1, "220", "0.75", "kava, sladkor"),  # Gostilna Pri Krki
    ("N-032", "C078", -2, 1, "160", "0.5", "podstavki, vrečke"),  # Kavarna Težka voda
    ("N-033", "C023", -3, 1, "700", "1.5", "moka, semena, kvas"),  # Gostilna Lipa
    ("N-034", "C024", -3, 1, "200", "0.5", "mleko, smetana"),  # Kavarna Sonce
    ("N-035", "C031", -3, 1, "650", "1.25", "moka T-850 20 vreč"),  # Pekarna Hlebec
    ("N-036", "C034", -3, 1, "150", "0.5", "čokolada, oreščki"),  # Slaščičarna Medenjak
    ("N-037", "C026", -3, 1, "180", "0.5", "čokolada, oreščki"),  # Slaščičarna Hmelj
    ("N-038", "C036", -3, 1, "800", "1.5", "sir 40 kg, mleko"),  # Gostilna Termalni vrelec
    ("N-039", "C030", -3, 1, "600", "1.25", "moka T-500 40 vreč"),  # Gostilna Hmeljar
    ("N-040", "C032", -3, 1, "550", "1", "moka, semena, kvas"),  # Kmečki turizem Zeleni breg
    ("N-041", "C035", -3, 1, "750", "1.5", "moka T-400 25 vreč"),  # Gostilna Pri Paki
    ("N-042", "C025", -3, 1, "900", "2", "moka T-500 40 vreč"),  # Restavracija Jezero
    ("N-043", "C028", -3, 1, "500", "1", "moka T-850 20 vreč"),  # Okrepčevalnica Smreka
    ("N-044", "C033", -3, 1, "700", "1.5", "moka T-850 20 vreč"),  # Gostilna Ob Savinji
    ("N-045", "C019", 0, 4, "530", "1", "olje, moka, sol"),  # Gostilna Goričko
    ("N-046", "C027", -2, 5, "500", "1", "olje, moka, sol"),  # Gostilna Pri kovaču
    ("N-047", "C029", -1, 2, "570", "1", "olje, moka, sol"),  # Restavracija Kristal
    ("N-048", "C037", -2, 2, "570", "1", "moka T-850 20 vreč"),  # Pekarna Pri mlinu
    ("N-049", "C039", -2, 2, "790", "1.5", "nadevi, embalaža"),  # Restavracija Barje
    ("N-050", "C040", -1, 1, "750", "1.5", "nadevi, embalaža"),  # Pekarna Slamnik
    ("N-051", "C041", -2, 1, "800", "1.5", "sladkor 20 vreč, kakav"),  # Gostilna Planinka
    ("N-052", "C042", -1, 1, "190", "0.5", "podstavki, vrečke"),  # Okrepčevalnica Močvirnik
    ("N-053", "C043", -3, 2, "140", "0.5", "embalaža"),  # Pekarna Sora
    ("N-054", "C044", -1, 4, "590", "1.25", "moka T-500 40 vreč"),  # Kmečki turizem Krim
    ("N-055", "C045", -1, 4, "290", "0.75", "mleko, smetana"),  # Slaščičarna Jagoda
    ("N-056", "C046", -1, 2, "410", "1", "sir 40 kg, mleko"),  # Gostilna Črni graben
    ("N-057", "C047", 0, 1, "190", "0.5", "sladkor, kakav"),  # Kavarna Ižanka
    ("N-058", "C048", -2, 5, "630", "1.25", "moka T-400 25 vreč"),  # Pekarna Jezerska
    ("N-059", "C049", 0, 2, "120", "0.25", "nadevi"),  # Kavarna Storžič
    ("N-060", "C050", -1, 5, "430", "1", "moka, sladkor, kvas"),  # Restavracija Stara pošta
    ("N-061", "C051", -2, 1, "170", "0.5", "moka, semena"),  # Slaščičarna Planika
    ("N-062", "C052", 0, 1, "740", "1.5", "moka T-850 20 vreč"),  # Gostilna Loški hrib
    ("N-063", "C053", -1, 2, "810", "1.5", "moka T-400 25 vreč"),  # Gostilna Pod Špikom
    ("N-064", "C054", -1, 1, "400", "1", "olje, moka, sol"),  # Kmečki turizem Bohinjka
    ("N-065", "C055", -1, 1, "220", "0.5", "čokolada, oreščki"),  # Slaščičarna Čebelica
    ("N-066", "C056", -2, 2, "750", "1.5", "moka T-500 40 vreč"),  # Gostilna Pri Radovni
    ("N-067", "C057", -2, 2, "300", "0.75", "embalaža"),  # Kavarna Draga
    ("N-068", "C058", -1, 2, "140", "0.5", "mleko, smetana"),  # Okrepčevalnica Ob Savi
    ("N-069", "C059", -2, 1, "660", "1.25", "olje, moka, sol"),  # Pekarna Soča
    ("N-070", "C060", -1, 1, "180", "0.5", "čokolada, oreščki"),  # Kavarna Burja
    ("N-071", "C061", 0, 2, "170", "0.5", "moka, semena"),  # Slaščičarna Čipka
    ("N-072", "C062", -3, 5, "570", "1.25", "sladkor 20 vreč, kakav"),  # Kmečki turizem Vipavska klet
    ("N-073", "C063", 0, 3, "210", "0.5", "moka, semena"),  # Okrepčevalnica Rožna dolina
    ("N-074", "C064", -3, 5, "280", "0.75", "mleko, smetana"),  # Kavarna Kanin
    ("N-075", "C065", -2, 4, "190", "0.5", "kvas, sol"),  # Pekarna Kanalka
    ("N-076", "C066", -3, 3, "900", "2", "olje, moka, sol"),  # Gostilna Brda
    ("N-077", "C067", -1, 3, "970", "2", "moka T-850 20 vreč"),  # Gostilna Pod Čavnom
    ("N-078", "C068", -1, 1, "540", "1", "sir 40 kg, mleko"),  # Restavracija Most
    ("N-079", "C069", -2, 2, "810", "1.5", "moka, sladkor, kvas"),  # Gostilna Pri vodnjaku
    ("N-080", "C072", -1, 1, "930", "2", "moka, semena, kvas"),  # Restavracija Trška gora
    ("N-081", "C073", -2, 3, "750", "1.5", "moka T-500 40 vreč"),  # Gostilna Cviček
    ("N-082", "C074", 0, 2, "260", "0.75", "kvas, sol"),  # Slaščičarna Bela krajina
    ("N-083", "C075", -1, 3, "690", "1.5", "moka, sladkor, kvas"),  # Pekarna Rog
    ("N-084", "C076", -2, 5, "230", "0.75", "sladkor, kakav"),  # Pekarna Temenica
    ("N-085", "C079", -2, 5, "600", "1.25", "moka, sladkor, kvas"),  # Gostilna Pod Gorjanci
    ("N-086", "C081", -2, 3, "760", "1.5", "moka, sladkor, kvas"),  # Pekarna Burin
    ("N-087", "C082", -1, 1, "410", "1", "moka, sladkor, kvas"),  # Restavracija Sidro
    ("N-088", "C083", 0, 1, "210", "0.5", "čokolada, oreščki"),  # Slaščičarna Školjka
    ("N-089", "C084", -3, 2, "560", "1", "moka T-500 40 vreč"),  # Kmečki turizem Teran
    ("N-090", "C085", -1, 1, "200", "0.5", "kvas, sol"),  # Okrepčevalnica Oljka
    ("N-091", "C086", -2, 1, "810", "1.5", "moka T-500 30 vreč"),  # Gostilna Kraški rob
    ("N-092", "C087", -1, 1, "430", "1", "moka T-500 40 vreč"),  # Gostilna Istrska hiša
    ("N-093", "C088", -1, 5, "190", "0.5", "sladkor, kakav"),  # Okrepčevalnica Pri meji
    ("N-094", "C089", -2, 3, "420", "1", "nadevi, embalaža"),  # Gostilna Refošk
    ("N-095", "C090", 0, 2, "450", "1", "sir 40 kg, mleko"),  # Restavracija Kraška jama
    ("N-096", "C091", -2, 4, "170", "0.5", "podstavki, vrečke"),  # Pekarna Istrska
    ("N-097", "C037", -1, 2, "2200", "6", "moka, sladkor, kvas"),  # Pekarna Pri mlinu
    ("N-098", "C048", 0, 3, "780", "1.5", "nadevi, embalaža"),  # Pekarna Jezerska
    ("N-099", "C059", -2, 1, "1500", "4.5", "moka, semena, kvas"),  # Pekarna Soča
    ("N-100", "C081", -4, -1, "960", "2", "sir 40 kg, mleko"),  # Pekarna Burin
]

TOURS = [
    # datum (dni od danes), vozilo, voznik, status, postanki: (naročilo, rezultat, razlog)
    # Pomurska, kombi
    (-1, "MB CD-456", DRIVER_MAJA_EMAIL, Tour.Status.COMPLETED, [
        ("N-001", Stop.Result.DELIVERED, ""),
        ("N-002", Stop.Result.DELIVERED, ""),
        ("N-003", Stop.Result.NOT_DELIVERED, "Stranka zaprta"),
        ("N-004", Stop.Result.DELIVERED, ""),
        ("N-005", Stop.Result.DELIVERED, ""),
        ("N-026", Stop.Result.DELIVERED, ""),
    ]),
    # Podravska, kombi
    (0, "MB AB-123", DRIVER_VID_EMAIL, Tour.Status.IN_DELIVERY, [
        ("N-006", Stop.Result.DELIVERED, ""),
        ("N-007", Stop.Result.DELIVERED, ""),
        ("N-008", Stop.Result.NOT_DELIVERED, "Ni bilo nikogar"),
        ("N-009", Stop.Result.PENDING, ""),
        ("N-010", Stop.Result.PENDING, ""),
        ("N-027", Stop.Result.PENDING, ""),
        ("N-028", Stop.Result.PENDING, ""),
    ]),
    # Savinjska, tovornjak
    (1, "MB TR-789", DRIVER_LUKA_EMAIL, Tour.Status.CONFIRMED, [
        ("N-033", Stop.Result.PENDING, ""),
        ("N-034", Stop.Result.PENDING, ""),
        ("N-035", Stop.Result.PENDING, ""),
        ("N-036", Stop.Result.PENDING, ""),
        ("N-037", Stop.Result.PENDING, ""),
        ("N-038", Stop.Result.PENDING, ""),
        ("N-039", Stop.Result.PENDING, ""),
        ("N-040", Stop.Result.PENDING, ""),
        ("N-041", Stop.Result.PENDING, ""),
        ("N-042", Stop.Result.PENDING, ""),
        ("N-043", Stop.Result.PENDING, ""),
        ("N-044", Stop.Result.PENDING, ""),
    ]),
    # Dolenjska, kombi, prvi dve naročili sta od iste stranke
    (1, "MB AB-123", DRIVER_VID_EMAIL, Tour.Status.DRAFT, [
        ("N-011", Stop.Result.PENDING, ""),
        ("N-012", Stop.Result.PENDING, ""),
        ("N-029", Stop.Result.PENDING, ""),
        ("N-030", Stop.Result.PENDING, ""),
        ("N-031", Stop.Result.PENDING, ""),
        ("N-032", Stop.Result.PENDING, ""),
    ]),
]

# Status naročila glede na rezultat postanka
ORDER_STATUS = {
    Stop.Result.PENDING: Order.Status.PLANNED,
    Stop.Result.DELIVERED: Order.Status.DELIVERED,
    Stop.Result.NOT_DELIVERED: Order.Status.NOT_DELIVERED,
}


class Command(BaseCommand):
    help = "Izbriše obstoječe ture, naročila, stranke in vozila ter naloži testne podatke"

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()
        now = timezone.now()

        # Najprej izbrišemo stare podatke, da lahko ukaz poženemo večkrat
        Stop.objects.all().delete()
        Tour.objects.all().delete()
        Order.objects.all().delete()
        Customer.objects.all().delete()
        Vehicle.objects.all().delete()
        User.objects.filter(email__in=OLD_EMAILS).delete()

        # Geslo zašifriramo samo enkrat, ker je šifriranje namenoma počasno
        password = make_password(SEED_PASSWORD)
        users = {}
        for email, first_name, last_name, role in USERS:
            users[email], _ = User.objects.update_or_create(
                email=email,
                defaults={
                    "first_name": first_name, "last_name": last_name, "role": role, "is_active": True,
                    "password": password,
                },
            )
        dispatcher = users[DISPATCHER_EMAIL]

        vehicles = {
            reg: Vehicle.objects.create(
                registration_number=reg, type=t, max_load_kg=kg, pallet_spaces=p, is_active=active
            )
            for reg, t, kg, p, active in VEHICLES
        }

        customers = {}
        for code, name, address, postal, city, region, lat, lng, contact, phone, note in CUSTOMERS:
            customer = Customer(
                code=code, name=name, address=address, postal_code=postal, city=city, region=region,
                lat=Decimal(lat), lng=Decimal(lng), contact_name=contact, phone=phone, delivery_note=note,
            )
            # Koordinate veljajo za ta naslov, zato jih ob dodajanju v turo ni treba iskati
            customer.geocoded_address = customer_address(customer)
            customer.save()
            customers[code] = customer

        orders = {}
        for number, code, received, deadline, weight, pallets, description in ORDERS:
            orders[number] = Order.objects.create(
                number=number,
                customer=customers[code],
                received_date=today + timedelta(days=received),
                dispatch_deadline=today + timedelta(days=deadline),
                weight_kg=Decimal(weight),
                pallets=Decimal(pallets),
                description=description,
            )

        for days, reg, driver_email, status, stops in TOURS:
            tour = Tour.objects.create(
                dispatch_date=today + timedelta(days=days),
                vehicle=vehicles[reg],
                driver=users[driver_email],
                created_by=dispatcher,
                status=status,
            )
            # Časi prehodov glede na status ture
            if status != Tour.Status.DRAFT:
                tour.confirmed_at = now - timedelta(days=2)
            if status in (Tour.Status.IN_DELIVERY, Tour.Status.COMPLETED):
                tour.started_at = now - timedelta(hours=4)
            if status == Tour.Status.COMPLETED:
                tour.completed_at = now - timedelta(hours=1)
            tour.save()

            for sequence, (number, result, reason) in enumerate(stops, start=1):
                order = orders[number]
                Stop.objects.create(
                    tour=tour,
                    order=order,
                    sequence=sequence,
                    result=result,
                    reason=reason,
                    marked_at=None if result == Stop.Result.PENDING else now - timedelta(hours=3 - sequence * 0.5),
                )
                order.status = ORDER_STATUS[result]
                order.save()

        settings = Settings.load()
        settings.warehouse_address = WAREHOUSE[0]
        settings.warehouse_lat = Decimal(WAREHOUSE[1])
        settings.warehouse_lng = Decimal(WAREHOUSE[2])
        settings.save()

        self.stdout.write(self.style.SUCCESS(
            f"Naloženo: {len(USERS)} uporabnikov, {len(VEHICLES)} vozil, {len(CUSTOMERS)} strank, "
            f"{len(ORDERS)} naročil, {len(TOURS)} ture. Geslo uporabnikov: {SEED_PASSWORD}"
        ))
