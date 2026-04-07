BIZNIS SPECIFIKACIJA
Aplikacija za osnovna sredstva i nematerijalna ulaganja
UniCore

| Verzija | 2.0 |
| --- | --- |
| Datum | 31. mart 2026. |
| Vlasnici dokumenta | Finansijsko i regulatorno izveštavanje, Upravljanje i održavanje poslovne imovine, IT Srvis |
| Product owners | Ivana Hadžić, Dejan Jovanović, Edita Jakupi |
| Status | In progress |

# 0. Uvod i pregled sistema

## 0.1. Svrha dokumenta

Ovaj dokument predstavlja biznis specifikaciju platforme za upravljanje osnovnim sredstvima (OS) i nematerijalnim ulaganjima (NU) banke. Specifikacija definiše sve poslovne procese, module, ekranske forme, prava pristupa, formule za obračun i izveštajne zahteve koji su neophodni za razvoj i implementaciju aplikacije.
Cilj dokumenta je da na strukturiran, jasan i sveobuhvatan način opiše poslovne zahteve, funkcionalne celine, korisničke uloge, obračunske mehanizme i izveštajne potrebe — kao osnovu za projektovanje i razvoj informacionog sistema.

## 0.2. Kontekst i obuhvat

Aplikacija UniCore se implementira za potrebe banke i obuhvata evidenciju, upravljanje i računovodstveno praćenje sledeće imovine:
- Osnovna sredstva (materijalna imovina)
- Nematerijalna ulaganja (softver, licence, interno generisana imovina)
- Ulaganja u tuđa osnovna sredstva (zakupljeni prostor)
- Investicione nekretnine (IAS 40)
Aplikacija UniCore treba da obezbedi:
- Centralizovanu evidenciju celokupne imovine banke
- Automatizovan obračun amortizacije (računovodstvene i poreske)
- Integraciju sa CORE sistemom banke putem interfejsa za slanje naloga za knjiženje
- Podršku za godišnji i vanredni popis imovine (skeniranje barkodova)
- Kompletno izveštavanje za sve korisničke uloge
- Optimizaciju postojećeg procesa
- Uvezivanje evidencije nematerijalnih ulaganja sa katalogom aplikacije banke
- Upload dokumentacije (odluka, zapisnika i slično)
- Integraciju sa Service central aplikacijom (SC)
- Generisanje reversa za izdavanje IT opreme zaposlenom (laptop i ostala oprema) kao i notifikacije zaposlenom o izdatoj opremi.

### 0.2.1. Postojeći proces

Trenutno se za evidenciju osnovnih sredstva i nematerijalna ulaganja banke koristi OSA aplikacija (vendora AB Soft) u kojoj se, pored evidencije osnovnih sredstava i nematerijalnih ulaganja vrši obračun amortizacije kao i projekcije amortizacije.
U OSA aplikaciji svi unosi/evidencije/aktivacije/isknjžavanja/promene lokacija i računopolagača se rade ručno, jedan po jedan unos a pristup aplikaciji imaju samo zaposleni iz računovodstva.
Pored evidencija u OSA aplikaciji, dosta evidencija se paralelno vodi u excel-u. IT ima deo evidencije u SC aplikaciji. Nalozi za aktiviranje se dostavljaju u excelu odakle se svako zasebno OS unosi u OSA aplikaciju. Promenu lokacija i slično računovodstvu dostavljaju kolege iz RE i IT kao popunjene excel file-ove odakle se podaci ručno unose u OSA aplikaciju.
Šematski prikaz osnovnog AS-IS procesa predstavljen je u dokumentu Prilog 1.

### 0.2.2. Budući proces

Šematski prikaz budućeg, TO-BE procesa predstavljen je u dokumentu Prilog 2.
Budući proces kroz novu platformu treba da optimizuje aktivnosti i ceo proces.

## 0.3. Korisnici aplikacije i prava pristupa

U aplikaciji postoje sledeće korisničke uloge sa definisanim pravima pristupa:

| Korisnička uloga | Prava pristupa |
| --- | --- |
| Računovodstvo (delegirani korisnici) | Pun pristup svim modulima i opcijama. Jedini korisnici koji mogu verifikovati unos. Korisnik iz računovodstva koji je uneo nalog NE može da verifikuje isti nalog — verifikaciju mora da izvrši drugi korisnik iz računovodstva. |
| ICT | Pristup modulu Nematerijalna ulaganja — pregled i unos (bez verifikacije). Pregled izveštaja koji se odnose na IT imovinu. Pristup modulu za Osnovna sredstva: aktivacije, promena lokacije. Pregled relevantnih izveštaja. |
| RE (Real Estate) | Pristup opcijama vezanim za nekretnine: ulaganja u tuđa OS, investicione nekretnine, promena lokacije. Pregled relevantnih izveštaja. |
| Tax | Pristup bazama osnovnih sredstava i nematerijalnih ulaganja (read-only) kao i poreskim izveštajima i obračunu poreske amortizacije. Mogućnost dinamičkog kreiranja izveštaja. |
| Controlling | Pristup projekcijama amortizacije i izveštajima po troškovnim centrima. Mogućnost dinamičkog kreiranja izveštaja. |
| Delegirani korisnici org. delova | Pristup podacima sopstvenog organizacionog dela: osnovna sredstva u pripremi, popis, promena lokacije i računopolagača. Mogućnost dinamičkog kreiranja izveštaja. |

## 0.4. Opšta pravila sistema

- Šifra korisnika dodeljuje se automatski na osnovu logovanog usera u svim opcijama.
- Datum pokretanja opcije automatski se dodeljuje gde je navedeno.
- Svaki nalog za knjiženje generiše se u modulu Izveštaji i šalje u CORE sistem banke putem interfejsa, nakon verifikacije korisnika iz računovodstva.
- Korisnik iz računovodstva koji unese nalog ne može da ga verifikuje — verifikaciju vrši drugi korisnik iz iste grupe.
- Kada se izvrši aktiviranje, uvećanje vrednosti, zamena rezervnog dela, osnovno sredstvo u pripremi ili investicija u toku, stavka dobija status Aktivirano.
- Popis se vrši na osnovu čitača (skenera) inventarskih brojeva. Nakon očitavanja, lokacija se automatski menja i evidentira na kartici OS sa opisom 'izmena po popisu'.
- Na osnovu definisanog konta OS u pripremi / investicije u toku vrši se kontrola ispravnosti kategorije OS.
- Moguća je izmena datuma aktiviranja i datuma početka obračuna amortizacije od strane korisnika iz računovodstva.
- Prilikom otpisa, prodaje i donacije osnovnog sredstva/nematerijalnog ulaganja, obračunata amortizacije u kalendarskoj godini u kojoj se sprovodi otpis, prodaja i donacije osnovnog sredstva/nematerijalnog ulaganja se pripisuje ispravci vrednosti konkretnog inventarskog broja.

## 0.5. Moduli aplikacije

Aplikacija za osnovna sredstva sadrži sledeće module:

| Modul | Opis |
| --- | --- |
| 1. Osnovna sredstva | Unos, aktivacija, upravljanje i raspolaganje osnovnim sredstvima |
| 2. Nematerijalna ulaganja | Unos, aktivacija i upravljanje nematerijalnim ulaganjima (softver, licence) |
| 3. Investicione nekretnine | Evidencija i vrednovanje investicionih nekretnina (IAS 40) |
| 4. Popis | Sprovođenje popisa imovine uz podršku čitača barkodova |
| 5. Obračuni | Mesečni, godišnji i poreski obračuni amortizacije; projekcije; revalorizacija |
| 6. Izveštaji | Kartice, baze, evidencije, nalozi za knjiženje, popisne liste, dinamički izveštaji |
| 7. Statički podaci | Šifarnici kategorija, lokacija, računopolagača, troškovnih centara i sl. |

## 0.6. Funkcionalnosti po MVP prioritetima

MVP 1 — Kritična osnova  (must have za lansiranje)

|  | Funkcionalnost / Modul | Opis |
| --- | --- | --- |
|  | Modul 1 – OS   Unos i aktivacija OS | Evidencija OS u pripremi, aktivacija sa automatskim inventarskim brojem, obračun amortizacione stope po kategoriji. Masovni uvoz iz Excel-a. |
|  | Modul 1 – OS   Otpis i prodaja OS | Otpis sa odlukom i spiskom inventarskih brojeva, promena statusa u 'Otpisano'. Prodaja sa prodajnom vrednošću, dokumentacijom (odluka, ugovor, zapisnik) i nalogom za knjiženje. |
|  | Modul 5 – Obračuni   Mesečni obračun amortizacije | Proporcionalna metoda, pokretanje ručno ili automatski (zakazani zadatak). Pregled pre potvrde, kreiranje naloga za knjiženje i automatsko slanje u CORE sistem banke. |
|  | Modul 7 – Šifarnici   Šifarnici i statički podaci | Kategorije OS/NU sa kontima, accountima i stopama amortizacije; lokacije, računopolagači, troškovni centri, organizacione jedinice, kontni plan, dobavljači, grupe poreske amortizacije. |
|  | Prava pristupa   Korisnička prava i tok verifikacije | Uloge: Računovodstvo (pun pristup), ICT, RE, Tax, Controlling, delegirani korisnici org. dela. Dvostepena verifikacija — korisnik koji unese nalog ne može ga verifikovati. |
|  | Modul 6 – Izveštaji   Kartica OS i baza OS | Kartica po inventarskom broju sa kompletnim istorijatom promena, baza aktivnih OS, evidencije otpisanih/prodatih/doniranih OS. Export u Excel i PDF za sve izveštaje. |

MVP 2 — Proširenje  (visok prioritet, prva iteracija)

|  | Funkcionalnost / Modul | Opis |
| --- | --- | --- |
|  | Modul 2 – NU   Nematerijalna ulaganja — aktivacija i upravljanje | Investicija u toku, aktivacija NU, uvećanje vrednosti, promena korisnog veka i metode amortizacije, isknjižavanje, otpis. Veza sa katalogom aplikacija banke. Aktivacija po komponentama. |
|  | Modul 1 – OS   Promena lokacije i računopolagača | Evidencija promene lokacije i računopolagača, automatski upis na karticu OS i u Izveštaj o kretanju OS. Podržan masovni uvoz iz Excel-a. |
|  | Modul 1 – OS   Ulaganje u tuđa OS | Unos i aktivacija ulaganja u zakupljeni prostor, amortizacija do isteka zakupa. Preračun stope amortizacije pri produženju perioda zakupa (aneks ugovora). |
|  | Modul 5 – Obračuni   Godišnji obračun i projekcije amortizacije | Godišnji zbir mesečnih obračuna po inventarskom broju, godišnji pripis ispravci vrednosti (31.03, 30.06, 30.09, 31.12). Projekcija po mesecima i godinama za zadati budući period. |
|  | Modul 6 – Izveštaji   Nalozi za knjiženje i integracija sa CORE | Generisanje naloga po modulima i opcijama, slanje u CORE sistem putem interfejsa. Nalozi međusobno povezani sa inventarskim brojevima OS. |
|  | Modul 1 – OS   Zamena rezervnog dela i isknjižavanje vrednosti | Zamena sa isknjiženjem po formuli (poznata/nepoznata NV dela), preračun amortizacione stope. Isknjižavanje NV i srazmernog dela IspV, ili samo IspV po zadatom iznosu. |

MVP 3 — Napredno  (druga iteracija razvoja)

|  | Funkcionalnost / Modul | Opis |
| --- | --- | --- |
|  | Modul 4 – Popis   Modul za popis sa skeniranjem barkodova | Pokretanje godišnjeg/vanrednog popisa, skeniranje barkoda/QR kodova ili ručni unos. Pregled razlika (poklapanje, lokacija izmenjena, manjak, višak), zaključivanje i generisanje zapisnika. |
|  | Modul 3 – IN   Investicione nekretnine (IAS 40) | Evidencija po modelu fer vrednosti, revalorizacija dva puta godišnje (30.06 i 31.12), kvartalno knjiženje kursnih razlika. Nalog za knjiženje prema CORE sistemu. |
|  | Modul 5 – Obračuni   Poreska amortizacija i revalorizacija | Odvojeni obračun poreske amortizacije prema stopama iz šifarnika kategorija. Metod revalorizacije za građevinske objekte u vlasništvu — dva puta godišnje, korisni vek svake godine 31.12. |
|  | Modul 6 – Izveštaji   Dinamički izveštaji i napredna pretraživanja | Slobodno kreiranje izveštaja po svim dostupnim poljima iz baze OS/NU/IN za zadati period. Pretraživanje po kontima, lokacijama, troškovnim centrima, računopolagačima i sl. |
|  | Modul 1 – OS   Donacija i otuđenje otpisanih OS | Donacija OS sa procenjenom vrednošću i obaveznom dokumentacijom (odluka, ugovor, zapisnik). Otuđenje otpisanih OS (deponija, reciklaža) sa zapisnikom o proceni i primopredaji. |
|  | Integracije   Integracija sa Service Central (SC) | Automatsko prosleđivanje aktiviranih IT OS u SC (inventarski broj, status, lokacija, računopolagač). Generisanje reversa za IT opremu i notifikacija zaposlenom o izdatoj opremi. |
|  | Dokumentacija Revers | Generisanje reversa za izdavanje IT opreme zaposlenom (laptop i ostala oprema) kao i notifikacije zaposlenom o izdatoj opremi |

## 0.7. Pain points

Svih 8 identifikovanih problema može se svesti na tri sistemska uzroka koje nova UniCore platforma direktno adresira.

| 01 Previše ručnog rada Pain pointi 01, 06, 08 | 02 Silosi podataka Pain pointi 02, 03, 07 | 03 Ograničen pristup Pain pointi 04, 05 |
| --- | --- | --- |

| 01 | Efikasnost   Sve se radi ručno, jedan po jedan OSA aplikacija ne podržava masovni unos. Svako osnovno sredstvo se unosi zasebno — aktivacije, isknjižavanja, promene lokacije i računopolagača sve se rade ručno, stavku po stavku. Novi sistem uvodi masovni uvoz iz Excel-a i automatizaciju. |
| --- | --- |

| 02 | Podaci   Rasparčana evidencija u tri sistema Paralelno postoje tri odvojene evidencije koje se ne sinhronizuju: OSA aplikacija, Excel fajlovi i Service Central (SC) za IT. |
| --- | --- |

| 03 | Procesi   Excel kao glavni kanal komunikacije IT i RE timovi šalju promene (lokacije, aktivacije) računovodstvu kao Excel fajlove. Računovodstvo ih zatim ručno prepisuje u OSA aplikaciju — dvostruki unos sa visokim rizikom od grešaka i gubitka podataka. |
| --- | --- |

| 04 | Pristup   Računovodstvo kao jedini korisnik postojeće aplikacije Samo zaposleni iz računovodstva mogu pristupiti OSA aplikaciji. ICT, RE, Tax i Controlling timovi potpuno zavise od računovodstva kao posrednika za svaki unos i svaku izmenu, što usporava procese i opterećuje jedan tim. |
| --- | --- |

| 05 | Integracija   Nema integracije sa CORE sistemom Nalozi za knjiženje se ne šalju automatski u CORE sistem. Proces knjiženja je potpuno manuelan i odvojen od evidencije imovine, što povećava rizik od neusklađenosti između računovodstvenih sistema. |
| --- | --- |

| 06 | Efikasnost   Popis bez tehnološke podrške Tokom godišnjeg popisa ne postoji automatsko ažuriranje lokacija po popisu niti sistemsko praćenje razlika (manjkovi, viškovi), već se evidencija zatečenog stanja vodi ručno u svesti, excel tabeli ili word dokumentu. |
| --- | --- |

| 07 | Podaci   NU nije vezano za katalog aplikacija Nematerijalna ulaganja (softver, licence) vode se odvojeno od IT kataloga aplikacija. |
| --- | --- |

| 08 | Efikasnost   Nema automatskog obračuna i projekcija Obračun amortizacije i projekcije korisnik mora da pokreće i prati rezultate. Nema automatskog zakazivanja ni notifikacija, što povećava rizik od propuštenih rokova. |
| --- | --- |

# Definicija formula i obračunskih pravila

## Proporcionalna (linearna) metoda amortizacije

Sve kategorije OS i NU amortizuju se proporcionalnom (linearnom) metodom. Amortizacija se obračunava počev od prvog dana nakon datuma početka obračuna amortizacije (koji automatski dobija vrednost poslednjeg dana u mesecu aktiviranja).

### Osnovna formula sadašnje vrednosti

| Sadašnja vrednost (SV) | Sadašnja vrednost (SV) |
| --- | --- |
| SV = NV - IspV | NV = Nabavna vrednost; IspV = Ukupno obračunata ispravka vrednosti (akumulirana amortizacija) |

| Mesečna amortizacija | Mesečna amortizacija |
| --- | --- |
| MA = (NV - RV) × Stopa / 12 | NV = Nabavna vrednost; RV = Rezidualna vrednost; Stopa = Godišnja stopa amortizacije iz kategorije |

| Godišnja stopa amortizacije | Godišnja stopa amortizacije |
| --- | --- |
| Stopa = 1 / KV × 100% | KV = Korisni vek trajanja u godinama (iz kategorije OS/NU) |

| Ispravka vrednosti (akumulirana amortizacija) | Ispravka vrednosti (akumulirana amortizacija) |
| --- | --- |
| IspV = Suma mesečnih amortizacija od datuma aktiviranja do obračunskog datuma | Kumulativni zbir svih obračunatih mesečnih amortizacija |

### Ulaganje u tuđa osnovna sredstva — amortizacija do isteka zakupa

Za ulaganja u tuđa osnovna sredstva, amortizacija se obračunava proporcionalnom metodom i raspodeljuje na period od prvog dana nakon datuma početka obračuna amortizacije do vrednosti polja Istek perioda zakupa.

| Mesečna amortizacija ulaganja u tuđa OS | Mesečna amortizacija ulaganja u tuđa OS |
| --- | --- |
| MA = NV / Broj meseci zakupa | Broj meseci zakupa = razlika u mesecima između Datuma početka obračuna amortizacije i Isteka perioda zakupa |

### Zamena rezervnog dela — formula isknjiženja

Pri zameni rezervnog dela razlikujemo dva slučaja:

| Slučaj A: Poznata nabavna vrednost dela koji se menja (popunjeno polje 'Nabavna vrednost dela koji se menja') |
| --- |

| Isknjižena NV dela | Isknjižena NV dela |
| --- | --- |
| ΔNVD = Uneta NV dela koji se menja | Direktno uneta vrednost |

| Isknjižena IspV dela | Isknjižena IspV dela |
| --- | --- |
| ΔIspVD = IspV × (ΔNVD / NV) | Srazmerni deo akumulirane amortizacije |

| Rashod — neotpisana vrednost dela | Rashod — neotpisana vrednost dela |
| --- | --- |
| Rashod = ΔNVD - ΔIspVD | Razlika između isknjižene NV i isknjižene IspV |

| Slučaj B: Nepoznata nabavna vrednost dela koji se menja (polje prazno) |
| --- |

| Odnos (procenat) dela | Odnos (procenat) dela |
| --- | --- |
| P = Vrednost novog rezervnog dela / NV OS | Udeo vrednosti rezervnog dela u ukupnoj NV |

| Isknjižena NV dela | Isknjižena NV dela |
| --- | --- |
| ΔNVD = NV × P |  |

| Isknjižena IspV dela | Isknjižena IspV dela |
| --- | --- |
| ΔIspVD = IspV × P |  |

| Rashod | Rashod |
| --- | --- |
| Rashod = ΔNVD - ΔIspVD |  |

U oba slučaja vrši se preračun nove amortizacione stope nakon zamene.

| Nova stopa amortizacije (nakon zamene) | Nova stopa amortizacije (nakon zamene) |
| --- | --- |
| Nova stopa = (Nova NV - RV) / Preostali korisni vek (meseci) | Nova NV = stara NV - ΔNVD + vrednost novog dela |

### Isknjižavanje vrednosti

| Isknjižavanje nabavne vrednosti i ispravke vrednosti | Isknjižavanje nabavne vrednosti i ispravke vrednosti |
| --- | --- |
| Rashod/Prihod = ΔNV - ΔIspV | ΔNV = iznos umanjenja NV; ΔIspV = srazmerni iznos ispravke vrednosti koji se isknjižava |

| Isknjižavanje samo ispravke vrednosti | Isknjižavanje samo ispravke vrednosti |
| --- | --- |
| Prihod = ΔIspV (zadati iznos) | Vrednost za koji se umanjuje IspV = prihod po bilansu uspeha |

### Donacija — sadašnja vrednost

| Sadašnja vrednost za donaciju | Sadašnja vrednost za donaciju |
| --- | --- |
| SV = NV - IspV - Obračunata amortizacija | Razlika nabavne vrednosti, ispravke vrednosti i ukupno obračunate amortizacije na datum donacije |

### Revalorizacija investicionih nekretnina

| Efekat revalorizacije | Efekat revalorizacije |
| --- | --- |
| ΔV = Nova fer vrednost - Sadašnja knjigovodstvena vrednost | ΔV > 0: prihod od revalorizacije; ΔV < 0: rashod od revalorizacije |

| Kursna razlika (tromesečno) | Kursna razlika (tromesečno) |
| --- | --- |
| KR = Fer vrednost × (Novi kurs - Stari kurs) | Vrednovanje na kraju svakog kvartala prema tekućem kursu |

# 1. Modul za osnovna sredstva

Modul za osnovna sredstva koristi se za unos osnovnih sredstava u pripremi i aktiviranje osnovnih sredstava.
U modulu za osnovna sredstva postoje sledeće opcije:
- Unos osnovnog sredstva
- U pripremi
- Aktivacija
- Zamena rezervnog dela
- Uvećanje vrednosti
- Isknjižavanje vrednosti
- Ulaganje u tuđa osnovna sredstva
- U pripremi
- Aktivacija
- Uvećanje vrednosti
- Otpis
- Otpis osnovnog sredstva
- Otpis ulaganja u tuđa osnovna sredstva
- Prodaja osnovnog sredstva
- Otuđenje otpisanih osnovnih sredstava
- Donacija osnovnog sredstva
- Promena lokacije i računopolagača osnovnog sredstva

## 1.1. Opcija Unos osnovnog sredstva

### 1.1.1. U pripremi

Unos osnovnih sredstava u pripremi vrši korisnik aplikacije iz računovodstva.
Kada se izabere podopcija osnovno sredstvo u pripremi, otvaraju se polja za unos:

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Oznaka OS u pripremi | Automatski / ručni | Automatski generiše sistem |
| Kategorija OS u pripremi | Padajući meni | Obavezno polje |
| Organizacioni deo | Padajući meni | Obavezno polje |
| Naziv dobavljača | Padajući meni | Obavezno polje |
| Broj dokumenta/fakture | Slobodan unos | Obavezno polje |
| Opis stavke | Slobodan unos | Obavezno polje |
| Nabavna vrednost | Numerički unos | Obavezno polje |
| Datum nabavke | Datum | Obavezno polje |
| Datum plaćanja | Datum |  |
| Konto | Automatski | Popunjava se na osnovu kategorije OS u pripremi |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

Na osnovu oznake OS u pripremi, iz ove podopcije moguće je pokrenuti: Aktivaciju, Zamenu rezervnog dela ili Uvećanje vrednosti.
Nakon unosa, potvrđuje se klikom na tab 'Unos završen'. Delegirani korisnici org. dela imaju pristup podacima samo svog dela; korisnici iz računovodstva imaju pristup svim podacima.

### 1.1.2. Aktivacija

Kada se izabere podopcija Aktivacija, otvaraju se polja za unos:

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Oznaka OS u pripremi | Padajući meni | Obavezno polje |
| Inventarski broj | Automatski | Dodeljuje se prvi slobodan inventarski broj |
| Naziv osnovnog sredstva | Slobodan unos | Obavezno polje |
| Kategorija OS | Padajući meni | Obavezno polje |
| Naziv dobavljača | Automatski | Prenosi se iz OS u pripremi |
| Broj dokumenta/fakture | Automatski | Prenosi se iz OS u pripremi |
| Konto OS | Automatski | Popunjava se iz kategorije OS |
| Datum nabavke/aktiviranja | Datum | Obavezno polje |
| Datum početka obračuna amortizacije | Automatski | Poslednji dan u mesecu aktiviranja |
| Nabavna vrednost | Numerički unos | Obavezno polje |
| Stopa amortizacije | Automatski | Popunjava se iz kategorije OS; u slučaju da je došlo do preračuna stope amortizacije upisuje se vrednost preračunate stope |
| Lokacija | Padajući meni | Obavezno polje |
| Računopolagač/odg. lice/org. deo | Padajući meni | Obavezno polje |
| Troškovni centar | Padajući meni | Obavezno polje |
| Serijski broj | Slobodan unos | Opciono |
| Količina | Numerički unos | Obavezno; ako > 1, vidi napomenu ispod |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

| Ako je unesena količina > 1, sistem automatski kreira onoliko inventarskih brojeva koliko iznosi vrednost polja Količina umanjena za 1, pri čemu se svi podaci kopiraju na sve kreirane inventarske brojeve. |
| --- |

Automatska kontrola: sistem poredi ukupnu NV aktiviranih OS sa ukupnom NV OS u pripremi prema broju dokumenta/fakture. Ako nema razlike → poruka 'Aktiviranje je uspešno sprovedeno'; ako postoji razlika → 'Postoji razlika između vrednosti nabavke po fakturi i aktivaciji'.
Podržan je uvoz iz Excel tabele.
Nakon potvrde unosa, korisnici iz računovodstva dobijaju notifikaciju. Korisnik iz računovodstva ima opcije: Verifikuj unos / Izmeni / Vrati na dopunu. Nakon verifikacije, podaci se upisuju na karticu OS i u bazu OS. Nalog za knjiženje se, na osnovu definisanog šablona, kreira u modulu Izveštaji i šalje u CORE sistem.
Omogućiti integraciju Aplikacija UniCore sa Service central (SC) aplikacijom na način da se aktivirano IT OS automatski prosleđuje u Service central, odnosno da se iz UniCore u SC prosleđuju vrednosti sledećih polja:

| Polje koje se prenose u SC | Napomena |
| --- | --- |
| Inventarski broj | Obavezan prenos |
| Naziv osnovnog sredstva | Opciono |
| Status | Obavezno |
| Kategorija OS | Opciono |
| Naziv dobavljača | Opciono |
| Datum nabavke/aktiviranja | Opciono |
| Lokacija | Obavezno - potencijalna sinhronizacija na npr. nedeljnom nivou (podatak unet u SC šalje u UniCore) |
| Računopolagač/odg. lice/org. deo | Opciono – potencijalna sinhronizacija na npr. nedeljnom nivou (podatak unet u SC šalje u UniCore) |
| Serijski broj | Slobodan unos |

### 1.1.3. Zamena rezervnog dela

Zamena rezervnog dela vrši se pojedinačno za svako osnovno sredstvo.

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Oznaka OS u pripremi | Slobodan unos / padajući | Obavezno polje |
| Kategorija OS | Padajući meni | Obavezno polje |
| Inventarski broj | Padajući meni | Bira se iz baze postojećih |
| Naziv OS | Automatski | Na osnovu inventarskog broja |
| Rezervni deo koji se menja | Slobodan unos | Opis dela |
| Naziv dobavljača | Automatski | Prenosi se iz OS u pripremi |
| Broj dokumenta/fakture | Automatski | Prenosi se iz OS u pripremi |
| Datum aktiviranja/zamene | Datum | Obavezno polje |
| Vrednost rezervnog dela | Numerički unos | Obavezno polje |
| NV dela koji se menja | Numerički unos | Opciono (vrednost pri inicijalnoj nabavci OS) |
| Stopa amortizacije | Automatski | Popunjava se iz kategorije OS; u slučaju da je došlo do preračuna stope amortizacije upisuje se vrednost preračunate stope |
| Serijski broj | Slobodan unos | Opciono |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

| Obračun isknjiženja: videti formule u poglavlju 'Definicija formula'. Nakon zamene vrši se preračun nove amortizacione stope od datuma aktiviranja. |
| --- |

Tok verifikacije identičan kao kod Aktivacije (Verifikuj / Izmeni / Vrati na dopunu → knjiženje u CORE).

### 1.1.4. Uvećanje vrednosti

Uvećanje vrednosti vrši se pojedinačno za svako osnovno sredstvo.

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Oznaka OS u pripremi | Slobodan unos | Obavezno polje |
| Kategorija OS | Padajući meni | Obavezno polje |
| Inventarski broj | Padajući meni | Bira se iz baze |
| Naziv OS | Automatski | Na osnovu inv. broja |
| Naziv dobavljača | Automatski | Prenosi se iz OS u pripremi |
| Broj dokumenta/fakture | Automatski | Prenosi se iz OS u pripremi |
| Opis ulaganja | Slobodan unos | Obavezno polje |
| Datum aktiviranja uvećanja vrednosti | Datum | Obavezno polje |
| Nabavna vrednost | Numerički unos | Obavezno polje |
| Stopa amortizacije | Automatski | Popunjava se iz kategorije OS; u slučaju da je došlo do preračuna stope amortizacije upisuje se vrednost preračunate stope |
| Serijski broj | Slobodan unos | Opciono |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

NV OS menja se od datuma aktiviranja. Tok verifikacije identičan kao kod Aktivacije.

### 1.1.5. Isknjižavanje vrednosti

Podopcija za isknjižavanje vrednosti OS po zadatom iznosu. Postoje dva načina:
- Isknjižavanje NV i srazmernog dela IspV: unosi se željeni iznos umanjenja NV. Sistem preračunava srazmerni deo IspV koji se isknjižava. Razlika (neotpisana vrednost) knjiži se kao rashod.
- Isknjižavanje samo IspV: unosi se iznos za umanjenje IspV. Taj iznos predstavlja prihod po bilansu uspeha.
Amortizaciona stopa preračunava se od datuma izmene u odnosu na novu NV i preostali korisni vek.

## 1.2. Ulaganje u tuđa osnovna sredstva

### 1.2.1. U pripremi

Unos ulaganja u tuđe osnovno sredstvo u pripremi vrši korisnik aplikacije iz računovodstva.

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Oznaka ulaganja u pripremi | Automatski / slobodan | Obavezno polje |
| Organizacioni deo | Padajući meni | Obavezno polje |
| Naziv dobavljača | Automatski | Prenosi se iz OS u pripremi |
| Broj dokumenta/fakture | Automatski | Prenosi se iz OS u pripremi |
| Opis stavke | Slobodan unos | Obavezno polje |
| Nabavna vrednost | Numerički unos | Obavezno polje |
| Datum nabavke | Datum | Obavezno polje |
| Datum plaćanja | Datum | opciono |
| Konto | Padajući meni | Obavezno polje |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

Na osnovu oznake ulaganja u pripremi može se pokrenuti opcija Aktivacija.

### 1.2.2. Aktivacija ulaganja u tuđa OS

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Oznaka ulaganja u pripremi | Padajući meni | Obavezno polje |
| Oznaka objekta u koji se vrši ulaganje | Padajući meni | Obavezno polje |
| Inventarski broj | Automatski | = Oznaka objekta + 'Ulaganje' |
| Redni broj ulaganja | Automatski | Naredni slobodan broj za dati inv. broj |
| Naziv ulaganja/opis stavke | Slobodan unos | Obavezno polje |
| Naziv dobavljača | Automatski | Iz ulaganja u pripremi |
| Broj dokumenta/fakture | Automatski | Iz ulaganja u pripremi |
| Datum nabavke/aktiviranja | Datum | Obavezno polje |
| Datum početka obračuna amortizacije | Automatski | Poslednji dan u mesecu u kojem se koristi opcija |
| Nabavna vrednost | Numerički unos | Obavezno polje |
| Rezidualna vrednost | Numerički unos | Opciono |
| Stopa amortizacije | Automatski | Popunjava se iz kategorije OS; u slučaju da je došlo do preračuna stope amortizacije upisuje se vrednost preračunate stope |
| Istek perioda zakupa | Automatski | Na osnovu oznake objekta |
| Lokacija | Padajući meni | Obavezno polje |
| Računopolagač/odg. lice/org. deo | Padajući meni | Obavezno polje |
| Troškovni centar | Padajući meni | Obavezno polje |
| Količina | Numerički unos | Obavezno polje |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

| Amortizacija se obračunava proporcionalnom metodom i raspodeljuje na period od prvog dana nakon datuma početka obračuna amortizacije do isteka perioda zakupa. U slučaju izmene perioda zakupa (produženja perioda zakupa usled aneksiranja ugovora i zakupu) potrebno je da se preračuna stopa amortizacije i prilagodi novom periodu isteka za zakupa za sva ulaganja čija je sadašnja vrednost različita od nule. |
| --- |

## 1.3. Otpis

### 1.3.1. Otpis osnovnog sredstva

Tabela za unos podataka:

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Inventarski broj | Padajući meni | Obavezno |
| Naziv OS | Automatski | Na osnovu inv. broja |
| Nabavna vrednost | Automatski | Prenosi se iz kartice OS |
| Ispravka vrednosti | Automatski | Obračunata akumulirana IspV |
| Obračunata amortizacija | Automatski | Ukupno obračunata amortizacija |
| Sadašnja vrednost | Automatski | = NV - IspV |
| Lokacija | Automatski | Na osnovu inv. broja |
| Datum otpisa | Automatski | Datum pokretanja opcije |
| Broj odluke | Ručni unos | Obavezno |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

Moguće je uneti više inventarskih brojeva. Podržan je uvoz iz Excel tabele.
Obavezna dokumentacija: Odluka o otpisu sa spiskom inventarskih brojeva.
Tok verifikacije: Verifikuj unos / Izmeni / Vrati na dopunu. Nakon verifikacije, OS dobija status Otpisan i premešta se u Evidenciju otpisanih OS (modul Izveštaji).

### 1.3.2. Otpis ulaganja u tuđa OS

Nakon izbora Oznake objekta iz padajućeg menija, otvara se tabela sa svim ulaganjima u taj objekat (inventarski broj, redni broj ulaganja, naziv, NV, IspV, obračunata amortizacija, sadašnja vrednost, lokacija, datum otpisa, broj odluke, šifra korisnika).
Obavezna dokumentacija: Odluka o otpisu ulaganja u tuđa OS sa spiskom inventarskih brojeva.
Tok verifikacije identičan kao kod Otpisa OS.

## 1.4. Prodaja osnovnog sredstva

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Inventarski broj | Padajući meni | Obavezno |
| Naziv OS | Automatski | Na osnovu inv. broja |
| Ukupna nabavna vrednost | Automatski | Prenosi se iz kartice OS |
| Ispravka vrednosti | Automatski | Obračunata akumulirana IspV |
| Obračunata amortizacija | Automatski | Ukupno obračunata amortizacija |
| Sadašnja vrednost | Automatski | = NV - IspV |
| Lokacija | Automatski | Na osnovu inv. broja |
| Datum prodaje | Automatski | Datum pokretanja opcije |
| Prodajna vrednost | Ručni unos | Obavezno |
| Broj odluke | Ručni unos | Obavezno |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

Moguće je uneti više inventarskih brojeva. Podržan je uvoz iz Excel tabele.
Obavezna dokumentacija: Odluka o prodaji sa spiskom inventarskih brojeva, Zapisnik o primopredaji, Ugovor o kupoprodaji.
Nalog za knjiženje nosi naziv: 'Nalog za knjiženje prodaje OS_[broj]_[datum]'.
Nakon verifikacije, OS se premešta iz baze aktivnih u evidenciju Prodatih OS. Količina OS dobija vrednost nula.

## 1.5. Otuđenje otpisanih osnovnih sredstava

Koristi se kada se otpisana OS fizički predaju trećem licu (deponija, reciklaža i sl.).

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Inventarski broj | Checkbox + izbor iz otpisanih | Iz izveštaja Otpisana OS |
| Naziv OS | Automatski | Na osnovu inv. broja |
| Broj odluke | Ručni unos | Obavezno |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

Podržan je uvoz iz Excel tabele. Obavezna dokumentacija: Odluka o otuđenju sa spiskom inventarskih brojeva, Zapisnik o proceni tržišne vrednosti, Zapisnik o primopredaji.
Nakon verifikacije, OS se premešta u izveštaj Otuđenih otpisanih OS. Količina OS dobija vrednost nula.

## 1.6. Donacija osnovnog sredstva

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Inventarski broj | Padajući meni | Obavezno |
| Naziv OS | Automatski | Na osnovu inv. broja |
| Nabavna vrednost | Automatski | Prenosi se iz kartice OS |
| Ispravka vrednosti | Automatski | Obračunata akumulirana IspV |
| Obračunata amortizacija | Automatski | Ukupno obračunata amortizacija |
| Sadašnja vrednost | Automatski | = NV - IspV - Obr. amortizacija |
| Lokacija | Automatski | Na osnovu inv. broja |
| Datum donacije | Automatski | Datum pokretanja opcije |
| Procenjena vrednost | Ručni unos | Obavezno |
| Broj odluke | Ručni unos | Obavezno |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

Podržan je uvoz iz Excel tabele.
Obavezna dokumentacija: Odluka o donaciji, Ugovor o donaciji, Zapisnik o proceni tržišne vrednosti, Zapisnik o primopredaji.
Nalog za knjiženje: 'Nalog za knjiženje donacije OS_[broj]_[datum]'.
Nakon verifikacije, OS se premešta u evidenciju Doniranih OS. Količina OS dobija vrednost nula.

## 1.7. Promena lokacije i računopolagača

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Inventarski broj | Padajući meni | Obavezno |
| Naziv OS | Automatski | Na osnovu inv. broja |
| Lokacija | Automatski | Trenutna lokacija |
| Nova lokacija | Padajući meni | Ako se ne izabere — ostaje stara lokacija |
| Računopolagač | Automatski | Trenutni računopolagač |
| Novi računopolagač | Padajući meni | Ako se ne izabere — ostaje stari |
| Datum | Automatski | Datum pokretanja opcije |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

Promena se evidentira bez pozadinskih preračuna. Podaci se upisuju u Izveštaj o kretanju OS i na karticu OS.
Podržan je uvoz iz Excel tabele.

# 2. Modul za nematerijalna ulaganja

Modul za nematerijalna ulaganja koristi se za unos investicija u toku i aktiviranje nematerijalnih ulaganja (softver, licence, interno generisana imovina).
Opcije modula:
- Unos nematerijalnog ulaganja:
- Investicija u toku
- Aktivacija
- Uvećanje vrednosti
- Promena korisnog veka i metode amortizacije
- Isknjižavanje vrednosti
- Otpis

## 2.1. Investicija u toku

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Oznaka investicije u toku | Automatski / slobodan | Obavezno polje |
| Kategorija NU | Padajući meni | Obavezno polje |
| Organizaciona jedinica | Padajući meni | Obavezno polje |
| Naziv dobavljača | Padajući meni | Obavezno polje |
| Broj dokumenta/fakture | Slobodan unos | Obavezno polje |
| Oznaka projekta | Slobodan unos | Obavezno ako je kategorija NU=UniC |
| Opis stavke | Slobodan unos | Obavezno polje |
| Nabavna vrednost | Numerički unos | Obavezno polje |
| Datum nabavke | Datum | Obavezno polje |
| Datum plaćanja | Datum | Obavezno polje |
| Konto | Automatski | Na osnovu kategorije NU |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

Iz ove podopcije može se pokrenuti Aktivacija ili Uvećanje vrednosti. Pristup imaju delegirani korisnici iz izabrane org. jedinice i svi korisnici iz računovodstva.

## 2.2. Aktivacija NU

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Oznaka investicije u toku | Padajući meni | Obavezno |
| Inventarski broj | Automatski | Prva slobodna vrednost za NU |
| Naziv nematerijalnog ulaganja | Slobodan unos | Obavezno |
| Kategorija NU | Padajući meni | Obavezno |
| Naziv dobavljača | Automatski | Iz investicije u toku |
| Broj dokumenta/fakture | Automatski | Iz investicije u toku |
| Oznaka projekta | Automatski | Iz investicije u toku |
| Konto NU | Automatski | Iz kategorije NU |
| Datum nabavke/aktiviranja | Datum | Obavezno |
| Datum početka obračuna amortizacije | Automatski | Poslednji dan u mesecu u kojem se vrši aktivacija |
| Nabavna vrednost | Numerički unos | Obavezno |
| Rezidualna vrednost | Numerički unos | Opciono |
| Stopa amortizacije | Automatski | Popunjava se iz kategorije OS; u slučaju da je došlo do preračuna stope amortizacije upisuje se vrednost preračunate stope |
| Lokacija | Padajući meni | Obavezno |
| Računopolagač/odg. lice/org. deo | Padajući meni | Defaultna vrdnost = ICT |
| Oznaka aplikacije iz kataloga aplikacija | Padajući meni | Obavezno |
| Troškovni centar | Padajući meni | Obavezno |
| Količina | Numerički unos | Obavezno – default vrednost=1 |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

Predviđena je mogućnost aktiviranja po komponentama ukoliko ulaganje ima više delova.

| Amortizacija se obračunava proporcionalnom metodom počev od prvog dana nakon datuma početka obračuna amortizacije. |
| --- |

## 2.3. Uvećanje vrednosti NU

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Oznaka investicije u toku | Padajući meni | Obavezno |
| Inventarski broj | Padajući meni | Iz baze postojećih NU |
| Naziv NU | Automatski | Na osnovu inv. broja |
| Kategorija NU | Automatski | Na osnovu inv. broja |
| Redni broj ulaganja | Automatski | Naredni slobodan broj za dati inv. broj |
| Naziv dobavljača | Automatski | Iz investicije u toku |
| Broj dokumenta/fakture | Automatski | Iz investicije u toku |
| Oznaka projekta | Slobodan unos | Obavezno ako je kategorija NU=UniC |
| Konto NU | Automatski | Iz kategorije NU |
| Datum nabavke/aktiviranja | Datum | Obavezno |
| Datum početka obračuna amortizacije | Automatski | Poslednji dan u mesecu u kojem se vrši aktivacija |
| Nabavna vrednost | Numerički unos | Obavezno |
| Rezidualna vrednost | Numerički unos | Opciono |
| Uticaj ulaganja na korisni vek trajanja | Numerički unos | Opciono; u mesecima |
| Stopa amortizacije | Automatski | Popunjava se iz kategorije OS; u slučaju da je došlo do preračuna stope amortizacije upisuje se vrednost preračunate stope |
| Lokacija | Automatski | Na osnovu inv. broja |
| Računopolagač/odg. lice/org. deo | Padajući meni | Defaultna vrdnost = ICT |
| Troškovni centar | Padajući meni | Obavezno |
| Oznaka aplikacije iz kataloga | Automatski | Na osnovu inv. broja |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

| Ako je popunjeno polje 'Uticaj ulaganja na korisni vek trajanja', sistem produžava korisni vek za uneti broj meseci i prilagođava amortizacionu stopu. Preračun amortizacije se vrši na prvi dan tekućeg kvartala (01.04., 01.07., 01.10., 01.01.) kako bi se efekat promene odrazio od početka tekućeg kvartala. Korisnik mora uneti obrazloženje promene korisnog veka u za to predviđeno polje. |
| --- |

## 2.4. Promena korisnog veka i metode amortizacije

Opcija omogućava izmenu korisnog veka upotrebe za izabrani inventarski broj NU, kao i sva njegova uvećanja vrednosti i sve ostale promene. Promena mora biti obrazložena izborom razloga iz unapred definisane kategorije razloga.
Nakon izmene, sistem prikazuje uporedni pregled obračuna amortizacije po novom i prethodnom korisnom veku trajanja pre nego što se promena potvrdi.

## 2.5. Isknjižavanje vrednosti NU

Identičan princip kao kod isknjižavanja vrednosti OS (videti tačku 1.1.5). Amortizaciona stopa preračunava se od datuma izmene.

## 2.6. Otpis NU

Procedura identična otpisu OS. Obavezna dokumentacija: Odluka o otpisu NU sa spiskom inventarskih brojeva.

# 3. Modul za investicione nekretnine

Modul se koristi za evidenciju i vrednovanje investicionih nekretnina banke u skladu sa MRS 40 (IAS 40).

## 3.1. Osnovna pravila

- Investicione nekretnine ne podležu obračunu amortizacije.
- Vrednuju se po modelu fer vrednosti (IAS 40, paragraf 33–55).
- Procena tržišne (fer) vrednosti vrši se dva puta godišnje: 30.06. i 31.12.
- Na kraju svakog kvartala vrši se vrednovanje za efekat kursa (knjiženje kursnih razlika).

## 3.2. Unos investicione nekretnine

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Inventarski broj | Automatski | Prva slobodna vrednost za kategoriju Investicione nekretnine |
| Naziv nekretnine | Slobodan unos | Obavezno |
| Kategorija | Padajući meni | Npr. poslovni prostor, stanovi, zemljište, garažna mesta |
| Lokacija | Padajući meni | Obavezno |
| Površina (m²) | Numerički unos | Opciono |
| Valuta | Padajući meni | Obavezno (RSD, EUR, ...) |
| Datum sticanja | Datum | Obavezno |
| Inicijalna nabavna vrednost | Numerički unos | Obavezno |
| Računopolagač/odg. lice | Padajući meni | Obavezno |
| Napomena | Slobodan unos | Opciono |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

## 3.3. Revalorizacija — procena fer vrednosti

Opcija za unos rezultata procene tržišne (fer) vrednosti vrši se dva puta godišnje (30.06. i 31.12.).

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Inventarski broj | Padajući meni | Obavezno |
| Datum procene | Datum | 30.06. ili 31.12. |
| Nova fer vrednost | Numerički unos | Obavezno — rezultat procene ovlašćenog procenitelja |
| Valuta | Padajući meni | Obavezno |
| Naziv procenitelja | Slobodan unos | Obavezno |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

| Formula: Efekat revalorizacije = Nova fer vrednost - Sadašnja knjigovodstvena vrednost. Pozitivna razlika = prihod od revalorizacije; negativna = rashod od revalorizacije. |
| --- |

Obavezna dokumentacija: Izveštaj o proceni tržišne vrednosti od ovlašćenog procenitelja.
Tok verifikacije: Verifikuj unos / Izmeni / Vrati na dopunu. Nakon verifikacije, nalog za knjiženje šalje se u CORE sistem.

## 3.4. Kursne razlike (tromesečno)

Na kraju svakog kvartala sistem vrši vrednovanje investicionih nekretnina denominovanih u stranoj valuti za efekat kursa.

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Inventarski broj | Padajući meni | Obavezno |
| Datum vrednovanja | Automatski | 31.03., 30.06., 30.09. ili 31.12. |
| Kurs na datum vrednovanja | Unos ili automatski preuzimanje | Zvanični kurs NBS |
| Prethodni kurs | Automatski | Kurs koji je korišćen u prethodnom vrednovanju |
| Knjgovodstvena vrednost | Automatski | Sadašnja vrednost u domaćoj valuti |
| Kursna razlika | Automatski | = Fer vrednost × (Novi kurs - Stari kurs) |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

# 4. Modul za popis

Modul za popis omogućava sprovođenje godišnjeg i vanrednog popisa osnovnih sredstava, nematerijalnih ulaganja i investicionih nekretnina uz podršku čitača (skenera) barkodova / QR kodova.

## 4.1. Pokretanje popisa

| Polje | Tip unosa | Napomena |
| --- | --- | --- |
| Vrsta popisa | Padajući meni | Godišnji popis / Vanredni popis |
| Datum popisa | Datum | Obavezno |
| Obuhvat | Padajući meni | Sva OS / po lokaciji / po org. delu / po kategoriji |
| Komisija za popis | Višestruki izbor | Biraju se članovi komisije iz šifarnika zaposlenih |
| Napomena | Slobodan unos | Opciono |
| Šifra korisnika | Automatski | Na osnovu logovanog usera |

Pokretanjem popisa, sistem generiše popisnu listu na osnovu izabranog obuhvata sa svim aktivnim OS/NU u evidenciji.

## 4.2. Sprovođenje popisa — skeniranje

Popis se vrši skeniranjem inventarskih brojeva (barkod / QR kod) čitačem. Sistem podržava i ručni unos inventarskog broja kao alternativu skeniranju.
- Nakon skeniranja inventarskog broja, sistem automatski evidentira:
- Datum i vreme skeniranja
- Korisnika koji je skenirao
- Lokaciju na kojoj je nađeno sredstvo (ako se razlikuje od evidentirane — vidi napomenu)
- Ako je OS pronađeno na drugoj lokaciji od evidentirane, sistem automatski menja lokaciju, upisuje izmenu na karticu OS i evidentira je u Izveštaju o promeni lokacije sa opisom 'izmena po popisu'.
- Korisnik može uneti napomenu/komentar za svaki popisani inventarski broj.

## 4.3. Pregled razlika

Po završetku skeniranja, sistem generiše izveštaj razlika koji prikazuje:

| Status | Opis |
| --- | --- |
| Popisano — poklapanje | Sredstvo pronađeno na evidentiranoj lokaciji |
| Popisano — lokacija izmenjena | Sredstvo pronađeno, lokacija automatski ažurirana |
| Nepopisano (manjak) | Sredstvo nije pronađeno — nije skenirano |
| Višak | Skeniran inventarski broj koji nije u evidenciji sistema |

## 4.4. Zaključivanje popisa

Nakon pregleda razlika, komisija potvrđuje popis. Sistem:
- Generiše finalni Zapisnik o popisu sa svim popisanim, nepopisanim i viškom OS
- Ažurira statuse i lokacije u bazi OS
- Premešta nepopisana sredstva u posebnu evidenciju za razmatranje (manjkovi)
- Kreira nalog za knjiženje eventualnih manjkova i viškova koji se šalje u CORE sistem

| Obavezna dokumentacija pri zaključenju: Zapisnik o popisu (generiše sistem) i Odluka komisije o razlikama. |
| --- |

## 4.5. Uvoz podataka za popis

Pored skeniranja, sistem podržava uvoz rezultata popisa iz Excel tabele sa kolonama: Inventarski broj, Lokacija pronalaska, Napomena.

# 5. Modul Obračuni

Aplikacija vrši sledeće obračune:

| Obračun | Opis i pravila |
| --- | --- |
| Mesečni obračun amortizacije | Obračun po svakom inventarskom broju za zadati datum. Primenjuje se proporcionalna metoda. Rezultat se evidentira po inventarskom broju i kategoriji. |
| Godišnji obračun amortizacije | Godišnji zbir mesečnih obračuna po svakom inventarskom broju. |
| Godišnji pripis amortizacije | Amortizacija obračunata u kalendarskoj godini pripisuje se ispravci vrednosti. Pripis se vrši za izabrani datum: 31.03., 30.06., 30.09. ili 31.12. |
| Grupni obračun amortizacije | Obračun amortizacije po kategorijama OS/NU — agregatni prikaz. |
| Obračun poreske amortizacije | Obračun prema stopama poreske amortizacije definisanim u šifarniku kategorija. Poreska stopa može se razlikovati od računovodstvene stope. |
| Projekcija amortizacije (mesečna) | Projekcija za zadati budući period, prikazana po mesecima, po svakom inventarskom broju. |
| Projekcija amortizacije (godišnja) | Projekcija za zadati budući period, prikazana po godinama, po svakom inventarskom broju. |
| Metod revalorizacije | Usklađivanje sa fer vrednošću za kategoriju OS Građevinski objekti u vlasništvu (metod revalorizacije, dva puta godišnje: 30.06. i 31.12.). Korisni vek upotrebe utvrđuje se svake godine 31.12. |

Pravila za obračun amortizacije:
- Obračun se pokreće mesečno, za poslednji dan u mesecu.
- Obračun amortizacije se može pokrenuti:
- - ručno  - od strane ovlašćenog korisnika za izabrani period
- - automatski - zakazanim zadatkom na tačno  određen datum
- Pre finalizacije korisnik pregleda obračun i potvrđuje ili odbija. Ako je obračun potvrđen, kreira se nalog za knjiženje i šalje u CORE sistem
- Osnovica za obračun amortizacije = nabavna vrednost − rezidualna vrednost
- Amortizacija prestaje kada sadašnja vrednost dostigne rezidualnu vrednost
- Pro-rata: za aktivaciju tokom meseca, amortizacija kreće od prvog dana narednog meseca
- Aplikacija podržava odvojeno računovodstvenu i poresku amortizaciju.

# 6. Modul Izveštaji

Modul Izveštaji obuhvata sledeće izveštaje i evidencije:

| Izveštaj | Opis |
| --- | --- |
| Kartica OS/NU po inventarskom broju | Sadrži sve elemente OS/NU kao i kompletan istorijski prikaz: naziv, broj, kategorija, NV, tržišna vrednost, datum aktivacije, sve promene i knjiženja, istorijat lokacija sa datumima promena i korisnicima koji su ih izvršili. |
| Pregled amortizacije za sva aktivna OS | Agregatni pregled obračunate amortizacije po svim aktivnim OS. |
| OS obrazac za statistiku | Standardizovani obrazac za potrebe statističkog izveštavanja. |
| Promene na kategorijama OS za period | Prikaz ulaza, izlaza i promena vrednosti po kategorijama OS za zadati period. |
| Promene na kategorijama NU za period | Prikaz ulaza, izlaza i promena vrednosti po kategorijama NU za zadati period. |
| Baza osnovnih sredstava | Pregled svih aktivnih OS sa svim atributima. |
| Baza nematerijalnih ulaganja | Pregled svih aktivnih NU sa svim atributima. |
| Baza investicionih nekretnina | Pregled svih investicionih nekretnina sa istorijskim vrednovanjima. |
| Izveštaj o OS/NU/IN u pripremi | Na osnovu izabrane org. jedinice — oznaka, dobavljač, faktura, opis, NV, datum nabavke, datum plaćanja. |
| Popisne liste | Po lokacijama / po računopolagačima / po kategorijama OS — za sprovođenje popisa. |
| Evidencija otpisanih OS | Sva otpisana OS sa datumima i odlukama o otpisu. |
| Evidencija otuđenih otpisanih OS | OS koja su fizički predata trećim licima nakon otpisa. |
| Evidencija prodatih OS | Sva prodata OS sa prodajnim vrednostima i dokumentacijom. |
| Evidencija doniranih OS | Sva donirana OS sa procenjenim vrednostima. |
| Izveštaj o kretanju OS | Promena lokacije i računopolagača po svakom individualnom OS — sa datumima i korisnicima. |
| Nalozi za knjiženje | Podeljeni po modulima i opcijama. Nalog za knjiženje i nalog za otpis/prodaju/donaciju moraju biti međusobno povezani. Svaki nalog ima svoj broj koji se upisuje uz inventarski broj OS. |
| Izveštaj o aktiviranim OS/NU za period | Obuhvata sva aktivirana OS/NU, zamene rezervnog dela i uvećanja vrednosti za izabrani period. |
| Izveštaj o isknjiženjima OS/NU | Pregled svih isknjižavanja vrednosti OS i NU. |
| Finansijski izveštaj po kontima | Izveštaj o nabavnoj vrednosti, ispravci vrednosti, obračunatoj amortizaciji i sadašnjoj vrednosti na zadati datum |
| Pretraživanja | Omogućiti pretraživanje po svakom dostupnom polju: po kontima, lokacijama, računopolagačima, troškovnim centrima i slično. |
| Dinamički izveštaj | Mogućnost slobodnog kreiranja izveštaja na bazi svih dostupnih polja iz baze OS/NU/IN za zadati period |

Za sve izveštaje omogućen je pregled, transfer u excel i pdf.

# 7. Statički podaci i šifarnici

Aplikacija sadrži sledeće šifarnike:

## 7.1. Kategorija OS

| Atribut | Opis |
| --- | --- |
| Naziv kategorije | Npr. Građevinski objekti, Oprema, Vozila... |
| Opis kategorije | Slobodan opis |
| Vrsta imovine | Materijalna / Nematerijalna |
| Konto OS | Konto osnovnog sredstva |
| Konto OS Core |  |
| Konto ispravke vrednosti |  |
| Konto amortizacije u toku |  |
| Konto rashoda amortizacije |  |
| Konto prihoda/rashoda od prodaje |  |
| Konto prihoda/rashoda od donacije |  |
| Konto prihoda/rashoda od otpisa |  |
| Account OS | CORE interni account |
| Account ispravke vrednosti |  |
| Account amortizacije u toku |  |
| Account rashoda amortizacije |  |
| Account prihoda/rashoda od prodaje |  |
| Account prihoda/rashoda od donacije |  |
| Account prihoda/rashoda od otpisa |  |
| Metod amortizacije | Proporcionalna (linearna) |
| Stopa amortizacije | Godišnja računovodstvena stopa (%) |
| Korisni vek trajanja | U godinama |
| Grupa poreske amortizacije | Prema poreskim propisima (%) |

## 7.2. Kategorija NU

Sadrži iste atribute kao Kategorija OS (videti 7.1). Nazivi kategorija NU: UniC software, Non UniC software, Licenca, Interno generisano.

## 7.3. Statusi

| Status | Uslov |
| --- | --- |
| Aktivno | Sadašnja vrednost ≠ 0 |
| Amortizovano | Sadašnja vrednost = 0 |
| Aktivirano | Prošlo kroz opciju aktivacije |
| Otpisano | Nakon verifikacije otpisa |
| Prodato | Nakon verifikacije prodaje |
| Donirano | Nakon verifikacije donacije |
| Otuđeno | Nakon verifikacije otuđenja otpisanog OS |
| Namenjeno prodaji | Manuelno postavljanje statusa |
| U pripremi | OS/NU je u fazi pripremi, još nije aktivirano |

## 7.4. Ostali šifarnici

| Šifarnik | Sadržaj |
| --- | --- |
| Kontni plan | Pregled svih konta sa nazivima, accountima, ICA kodovima i nazivima ICA kodova |
| Troškovni centri | Broj TC, naziv TC, organizaciona jedinica, struktura |
| Grupe poreske amortizacije | Poreska grupa, naziv poreske grupe, poreska stopa |
| Organizacione jedinice | Šifra, naziv, hijerarhijska struktura |
| Lokacije | Šifra, naziv, adresa, organizaciona jedinica |
| Računopolagači | Šifra, ime i prezime, organizaciona jedinica, aktivan/neaktivan |
| Katalog aplikacija | Oznaka aplikacije, naziv, vlasnik, tip (UniC/Non UniC/Interno) |
| Dobavljači | Naziv, PIB, adresa |
| Zaposleni/Komisija | Za potrebe definisanja komisije za popis |
| Razlozi promene korisnog veka | Unapred definisane kategorije razloga za promenu KV (NU) |
| Registar objekata zakupa | Oznaka objekta, naziv, istek zakupa, zakupodavac, lokacija — za ulaganja u tuđa OS |

# Prilog: Pregled tokova verifikacije

Sve opcije koje zahtevaju verifikaciju prate sledeći standardni tok:

| Korak | Opis |
| --- | --- |
| 1. Unos i potvrda | Korisnik unosi podatke i potvrđuje klikom na tab 'Unos završen'. Ako nedostaje obavezna dokumentacija → poruka 'Unos nije kompletan'. |
| 2. Notifikacija | Korisnici iz računovodstva dobijaju automatsku notifikaciju o novom nalogu. |
| 3. Pregled naloga | Korisnik iz računovodstva vidi sve unete podatke i priloženu dokumentaciju. |
| 4a. Verifikacija | Klikom na 'Verifikuj unos' — podaci se upisuju u bazu, status se menja, kreira se nalog za knjiženje. |
| 4b. Izmena | Korisnik iz računovodstva može direktno izmeniti podatke. |
| 4c. Povrat na dopunu | Korisnik iz računovodstva vraća nalog sa komentarom razloga — korisnik koji je uneo nalog dobija notifikaciju. |
| 5. Slanje u CORE | Nalog za knjiženje se, nakon verifikacije korisnika iz računovodstva, putem interfejsa šalje u CORE sistem banke. |

| Napomena: Korisnik koji je uneo nalog NE MOŽE da ga verifikuje — verifikaciju mora izvršiti drugi korisnik iz grupe računovodstvo. Ovo pravilo se primenjuje za: aktivaciju, otpis, prodaju, donaciju, otuđenje otpisanih OS. |
| --- |
