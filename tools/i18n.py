# -*- coding: utf-8 -*-
"""
Generator wersji językowych strony Narnia Glamp.

Źródłem jest polska strona index.html. Skrypt tworzy en/index.html i de/index.html,
podmieniając polskie teksty na tłumaczenia z listy PAIRS (pl, en, de).

Użycie (z katalogu głównego repozytorium):
    python3 tools/i18n.py

Po każdej zmianie tekstów w index.html uruchom skrypt ponownie. Jeśli jakiś polski tekst
z listy nie zostanie znaleziony albo w wyniku zostaną polskie znaki, skrypt to wypisze.
"""
import re, sys, base64, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANGS = ["en", "de"]

# (pl, en, de) — dokładne fragmenty z index.html. Dłuższe fragmenty są podmieniane jako pierwsze.
PAIRS = [
# ---------- <head> ----------
('content="Narnia Glamp – dom na odludziu na wyłączność"',
 'content="Narnia Glamp – a secluded house all to yourselves"',
 'content="Narnia Glamp – ein abgelegenes Haus ganz für Sie allein"'),
('content="Leśniczówka na 2 ha nad Bobrem: sauna, balia, stodoła, tipi, rowery, plaża. Cały teren tylko dla Was."',
 'content="A former forester\'s lodge on 2 ha by the Bóbr river: sauna, hot tub, barn, tipi, bikes, beach. The whole grounds just for you."',
 'content="Ehemaliges Forsthaus auf 2 ha am Fluss Bóbr: Sauna, Badezuber, Scheune, Tipi, Fahrräder, Strand. Das ganze Gelände nur für Sie."'),
('content="Narnia – dom wakacyjny na odludziu w Krzywej nad Bobrem. Cały teren 2 ha na wyłączność: sauna, balia, stodoła, tipi, rowery, plaża."',
 'content="Narnia – a secluded holiday house in Krzywa by the Bóbr river, western Poland. 2 ha exclusively yours: sauna, hot tub, barn, tipi, bikes, beach."',
 'content="Narnia – abgelegenes Ferienhaus in Krzywa am Bóbr (Bober), Westpolen, nahe der deutschen Grenze. 2 ha exklusiv für Sie: Sauna, Badezuber, Scheune, Tipi, Fahrräder, Strand."'),
('Część zdjęć nie wczytała się. Odśwież stronę albo uruchom skrypt pobierający zdjęcia.',
 'Some photos did not load. Please refresh the page.',
 'Einige Fotos wurden nicht geladen. Bitte laden Sie die Seite neu.'),

# ---------- nagłówek ----------
('aria-label="Narnia – początek strony"', 'aria-label="Narnia – top of page"', 'aria-label="Narnia – Seitenanfang"'),
('aria-label="Narnia na Instagramie"', 'aria-label="Narnia on Instagram"', 'aria-label="Narnia auf Instagram"'),
('aria-controls="nav">Menu</button>', 'aria-controls="nav">Menu</button>', 'aria-controls="nav">Menü</button>'),
('<a href="#dom">Dom i teren</a>', '<a href="#dom">House &amp; grounds</a>', '<a href="#dom">Haus &amp; Gelände</a>'),
('<a href="#czas">Czas w Narnii</a>', '<a href="#czas">Time in Narnia</a>', '<a href="#czas">Zeit in Narnia</a>'),
('<a href="#wyprawy">Wyprawy</a>', '<a href="#wyprawy">Trips</a>', '<a href="#wyprawy">Ausflüge</a>'),
('<a href="#galeria">Galeria</a>', '<a href="#galeria">Gallery</a>', '<a href="#galeria">Galerie</a>'),
('<a href="#wydarzenia">Wydarzenia</a>', '<a href="#wydarzenia">Events</a>', '<a href="#wydarzenia">Events</a>'),
('<a href="#cennik">Cennik</a>', '<a href="#cennik">Prices</a>', '<a href="#cennik">Preise</a>'),
('<a href="#kontakt">Kontakt</a>\n    </nav>', '<a href="#kontakt">Contact</a>\n    </nav>', '<a href="#kontakt">Kontakt</a>\n    </nav>'),
('<a class="btn" href="#kalkulator">Sprawdź cenę</a>', '<a class="btn" href="#kalkulator">Check price</a>', '<a class="btn" href="#kalkulator">Preis berechnen</a>'),

# ---------- hero ----------
('<span class="eyebrow">Krzywa · dolina Bobru · lubuskie</span>',
 '<span class="eyebrow">Krzywa · Bóbr valley · western Poland</span>',
 '<span class="eyebrow">Krzywa · Bobertal · Westpolen</span>'),
('<h1>Dom na odludziu. <em>Cały dla Was.</em></h1>',
 '<h1>A house in the wild. <em>All yours.</em></h1>',
 '<h1>Ein Haus in der Wildnis. <em>Ganz für Sie.</em></h1>'),
('Leśniczówka na dwóch hektarach, bez sąsiadów, z sauną, balią, stodołą i plażą. Zawsze wynajmujemy cały teren na wyłączność.',
 'A former forester\'s lodge on two hectares with no neighbours, a sauna, a hot tub, a barn and a beach. We always rent out the whole property exclusively.',
 'Ein ehemaliges Forsthaus auf zwei Hektar ohne Nachbarn, mit Sauna, Badezuber, Scheune und Strand. Wir vermieten immer das gesamte Gelände exklusiv.'),
('<span id="seasonTxt">Sezon</span>', '<span id="seasonTxt">Season</span>', '<span id="seasonTxt">Saison</span>'),
('Minimalny okres najmu: 2 doby, latem 3 doby.', 'Minimum stay: 2 nights, in summer 3 nights.', 'Mindestaufenthalt: 2 Nächte, im Sommer 3 Nächte.'),
('<a class="btn" href="#kalkulator">Policz cenę pobytu</a>', '<a class="btn" href="#kalkulator">Calculate your price</a>', '<a class="btn" href="#kalkulator">Preis berechnen</a>'),
('<a class="btn ghost" href="#galeria">Zobacz zdjęcia</a>', '<a class="btn ghost" href="#galeria">See photos</a>', '<a class="btn ghost" href="#galeria">Fotos ansehen</a>'),
('data-label="Narnia z lotu ptaka" data-alt="Narnia z lotu ptaka: zabudowania, kanał i lasy po horyzont"',
 'data-label="Narnia from above" data-alt="Narnia from above: buildings, the canal and forest to the horizon"',
 'data-label="Narnia von oben" data-alt="Narnia von oben: Gebäude, Kanal und Wald bis zum Horizont"'),
('<span>miejsc w domu i w 2 namiotach glampingowych</span>', '<span>beds in the house and 2 glamping tents</span>', '<span>Schlafplätze im Haus und in 2 Glampingzelten</span>'),
('<span>terenu tylko dla Was</span>', '<span>of grounds just for you</span>', '<span>Gelände nur für Sie</span>'),
('<span>rowerów dla dorosłych + 4 dziecięce</span>', '<span>adult bikes + 4 for kids</span>', '<span>Fahrräder für Erwachsene + 4 für Kinder</span>'),
('<span>osób w saunie i 8 w balii</span>', '<span>people in the sauna, 8 in the hot tub</span>', '<span>Personen in der Sauna, 8 im Badezuber</span>'),

# ---------- welcome ----------
('<blockquote>Narnia to coś więcej niż dom wakacyjny.</blockquote>',
 '<blockquote>Narnia is more than a holiday house.</blockquote>',
 '<blockquote>Narnia ist mehr als ein Ferienhaus.</blockquote>'),
('To miejsce, w którym przeżyjecie niezapomniane chwile, odzyskacie równowagę i wrócicie do magii z dziecięcych marzeń.',
 'It\'s a place for unforgettable moments, for finding your balance again and returning to the magic of childhood dreams.',
 'Ein Ort für unvergessliche Momente, um wieder ins Gleichgewicht zu kommen und zur Magie der Kindheitsträume zurückzukehren.'),
('Z dala od hałasu i sąsiadów, z widokami, które zostają w pamięci. Za płotem setki hektarów lasu, kilka minut pieszo do dzikiej plaży nad Bobrem.',
 'Far from noise and neighbours, with views you will remember. Hundreds of hectares of forest beyond the fence and a wild beach on the Bóbr just a few minutes\' walk away.',
 'Weit weg von Lärm und Nachbarn, mit Ausblicken, die man nicht vergisst. Hinter dem Zaun Hunderte Hektar Wald, ein paar Gehminuten bis zum wilden Strand am Bober.'),

# ---------- dom ----------
('<span class="eyebrow">Dom i teren</span>', '<span class="eyebrow">House &amp; grounds</span>', '<span class="eyebrow">Haus &amp; Gelände</span>'),
('<h2>Leśniczówka dla całej ekipy</h2>', '<h2>A forester\'s lodge for the whole crew</h2>', '<h2>Ein Forsthaus für die ganze Gruppe</h2>'),
('Wiosną i latem do 12 osób w domu, do tego dwa namioty glampingowe na 3 i 4 osoby oraz pole kempingowe.',
 'In spring and summer up to 12 people in the house, plus two glamping tents for 3 and 4 people and a camping field.',
 'Im Frühling und Sommer bis zu 12 Personen im Haus, dazu zwei Glampingzelte für 3 und 4 Personen und eine Zeltwiese.'),
('id="tab-dom">W domu</button>', 'id="tab-dom">In the house</button>', 'id="tab-dom">Im Haus</button>'),
('id="tab-zew">Na zewnątrz</button>', 'id="tab-zew">Outdoors</button>', 'id="tab-zew">Draußen</button>'),
('<span>miejsc do spania wiosną i latem: 12 w domu i 7 w namiotach glampingowych, plus pole kempingowe. Cena domu obejmuje 10 osób, każda kolejna to 100 zł za noc.</span>',
 '<span>beds in spring and summer: 12 in the house and 7 in glamping tents, plus a camping field. The house price covers 10 people; each additional person is 100 zł (25 €) per night.</span>',
 '<span>Schlafplätze im Frühling und Sommer: 12 im Haus und 7 in Glampingzelten, dazu eine Zeltwiese. Der Hauspreis gilt für 10 Personen, jede weitere kostet 100 zł (25 €) pro Nacht.</span>'),

# ---------- czas w Narnii ----------
('<span class="eyebrow">Czas w Narnii</span>', '<span class="eyebrow">Time in Narnia</span>', '<span class="eyebrow">Zeit in Narnia</span>'),
('<h2>Co Was czeka</h2>', '<h2>What awaits you</h2>', '<h2>Was Sie erwartet</h2>'),
('Wybierz porę roku, a podświetlimy to, co wtedy smakuje najlepiej.',
 'Pick a season and we\'ll highlight what\'s best at that time of year.',
 'Wählen Sie eine Jahreszeit und wir zeigen, was dann am schönsten ist.'),
('data-season="all" aria-pressed="false">Wszystko</button>', 'data-season="all" aria-pressed="false">All</button>', 'data-season="all" aria-pressed="false">Alles</button>'),
('data-season="lato" aria-pressed="false">Lato</button>', 'data-season="lato" aria-pressed="false">Summer</button>', 'data-season="lato" aria-pressed="false">Sommer</button>'),
('data-season="jesien" aria-pressed="false">Jesień</button>', 'data-season="jesien" aria-pressed="false">Autumn</button>', 'data-season="jesien" aria-pressed="false">Herbst</button>'),
('data-season="zima" aria-pressed="false">Zima</button>', 'data-season="zima" aria-pressed="false">Winter</button>', 'data-season="zima" aria-pressed="false">Winter</button>'),
('data-season="wiosna" aria-pressed="false">Wiosna</button>', 'data-season="wiosna" aria-pressed="false">Spring</button>', 'data-season="wiosna" aria-pressed="false">Frühling</button>'),

# ---------- wyprawy ----------
('<span class="eyebrow">Wyprawy wokół Narnii</span>', '<span class="eyebrow">Trips around Narnia</span>', '<span class="eyebrow">Ausflüge rund um Narnia</span>'),
('<h2>W którąkolwiek stronę nie wyjdziesz, będzie pięknie</h2>', '<h2>Whichever way you go, it\'s beautiful</h2>', '<h2>Egal in welche Richtung – es ist wunderschön</h2>'),
('Szczególnie polecamy spacer na dziką plażę.', 'We especially recommend the walk to the wild beach.', 'Besonders empfehlen wir den Spaziergang zum wilden Strand.'),
('<h3 style="margin-bottom:16px">Pieszo</h3>', '<h3 style="margin-bottom:16px">On foot</h3>', '<h3 style="margin-bottom:16px">Zu Fuß</h3>'),
('<h3 style="margin-bottom:16px">Rowerem</h3>', '<h3 style="margin-bottom:16px">By bike</h3>', '<h3 style="margin-bottom:16px">Mit dem Fahrrad</h3>'),

# ---------- galeria ----------
('<span class="eyebrow">Galeria</span>', '<span class="eyebrow">Gallery</span>', '<span class="eyebrow">Galerie</span>'),
('<h2>Narnia o każdej porze</h2>', '<h2>Narnia in every season</h2>', '<h2>Narnia zu jeder Jahreszeit</h2>'),
('id="moreBtn">Pokaż więcej zdjęć</button>', 'id="moreBtn">Show more photos</button>', 'id="moreBtn">Mehr Fotos zeigen</button>'),
('<strong>Zobacz, co dzieje się w Narnii teraz</strong><span>Śledź nas na Instagramie: @narniaglamp</span>',
 '<strong>See what\'s happening in Narnia right now</strong><span>Follow us on Instagram: @narniaglamp</span>',
 '<strong>Sehen Sie, was gerade in Narnia passiert</strong><span>Folgen Sie uns auf Instagram: @narniaglamp</span>'),
('<span class="ig-go">Obserwuj →</span>', '<span class="ig-go">Follow →</span>', '<span class="ig-go">Folgen →</span>'),

# ---------- cennik ----------
('<span class="eyebrow">Cennik</span>', '<span class="eyebrow">Prices</span>', '<span class="eyebrow">Preise</span>'),
('<h2>Cena za dobę za cały obiekt</h2>', '<h2>Price per night for the whole property</h2>', '<h2>Preis pro Nacht für das gesamte Anwesen</h2>'),
('Do 10 osób w cenie. <strong>Minimalny okres najmu to 2 doby, a latem (lipiec–sierpień) 3 doby.</strong> Jednorazowe sprzątanie 400 zł.',
 'Up to 10 people included. <strong>Minimum stay is 2 nights, in summer (July–August) 3 nights.</strong> One-off cleaning fee 400 zł (100 €).',
 'Bis zu 10 Personen inklusive. <strong>Mindestaufenthalt 2 Nächte, im Sommer (Juli–August) 3 Nächte.</strong> Einmalige Endreinigung 400 zł (100 €).'),
('<header><h3>Sezon wysoki</h3><small>maj – wrzesień</small></header>', '<header><h3>High season</h3><small>May – September</small></header>', '<header><h3>Hauptsaison</h3><small>Mai – September</small></header>'),
('<dl><dt>Weekendy i święta</dt><dd>1800 zł</dd><dt>Dni SLOW (pon–czw)</dt><dd>1300 zł</dd></dl>',
 '<dl><dt>Weekends &amp; holidays</dt><dd>1800 zł (450 €)</dd><dt>SLOW days (Mon–Thu)</dt><dd>1300 zł (325 €)</dd></dl>',
 '<dl><dt>Wochenenden &amp; Feiertage</dt><dd>1800 zł (450 €)</dd><dt>SLOW-Tage (Mo–Do)</dt><dd>1300 zł (325 €)</dd></dl>'),
('<header><h3>Sezon niski</h3><small>październik – kwiecień</small></header>', '<header><h3>Low season</h3><small>October – April</small></header>', '<header><h3>Nebensaison</h3><small>Oktober – April</small></header>'),
('<dl><dt>Weekendy i święta</dt><dd>1600 zł</dd><dt>Dni SLOW (pon–czw)</dt><dd>1200 zł</dd></dl>',
 '<dl><dt>Weekends &amp; holidays</dt><dd>1600 zł (400 €)</dd><dt>SLOW days (Mon–Thu)</dt><dd>1200 zł (300 €)</dd></dl>',
 '<dl><dt>Wochenenden &amp; Feiertage</dt><dd>1600 zł (400 €)</dd><dt>SLOW-Tage (Mo–Do)</dt><dd>1200 zł (300 €)</dd></dl>'),
('<header><h3>Namioty glampingowe i pole kempingowe</h3><small>wiosna – lato</small></header>',
 '<header><h3>Glamping tents &amp; camping field</h3><small>spring – summer</small></header>',
 '<header><h3>Glampingzelte &amp; Zeltwiese</h3><small>Frühling – Sommer</small></header>'),
('<dl><dt>Namiot glampingowy na 3 osoby</dt><dd id="pG3"></dd><dt>Namiot glampingowy na 4 osoby</dt><dd id="pG4"></dd><dt>Pole kempingowe (własny namiot lub kamper)</dt><dd>60 zł (15 €) / os. / noc</dd></dl>',
 '<dl><dt>Glamping tent for 3</dt><dd id="pG3"></dd><dt>Glamping tent for 4</dt><dd id="pG4"></dd><dt>Camping field (own tent or camper)</dt><dd>60 zł (15 €) / person / night</dd></dl>',
 '<dl><dt>Glampingzelt für 3 Personen</dt><dd id="pG3"></dd><dt>Glampingzelt für 4 Personen</dt><dd id="pG4"></dd><dt>Zeltwiese (eigenes Zelt oder Camper)</dt><dd>60 zł (15 €) / Person / Nacht</dd></dl>'),
('<strong>Namioty glampingowe i pole kempingowe są dostępne wyłącznie jako rozszerzenie wynajmu domu.</strong>',
 '<strong>Glamping tents and the camping field are only available as an add-on to renting the house.</strong>',
 '<strong>Glampingzelte und Zeltwiese gibt es nur zusätzlich zur Miete des Hauses.</strong>'),
('Osoby śpiące w namiotach glampingowych nie płacą za pole kempingowe. Dzieci do 4 lat gratis.',
 'Guests sleeping in glamping tents don\'t pay for the camping field. Children up to 4 stay free.',
 'Wer im Glampingzelt schläft, zahlt nicht für die Zeltwiese. Kinder bis 4 Jahre kostenlos.'),
('<span class="eyebrow">Kalkulator pobytu</span><h3 style="margin-top:6px">Policz swój termin</h3>',
 '<span class="eyebrow">Stay calculator</span><h3 style="margin-top:6px">Price your dates</h3>',
 '<span class="eyebrow">Preisrechner</span><h3 style="margin-top:6px">Ihren Termin berechnen</h3>'),
('role="group" aria-label="Waluta"', 'role="group" aria-label="Currency"', 'role="group" aria-label="Währung"'),
('<label for="dIn">Przyjazd</label>', '<label for="dIn">Arrival</label>', '<label for="dIn">Anreise</label>'),
('<label for="dOut">Wyjazd</label>', '<label for="dOut">Departure</label>', '<label for="dOut">Abreise</label>'),
('<span class="fs-label" id="lg">Osoby w domu</span>', '<span class="fs-label" id="lg">People in the house</span>', '<span class="fs-label" id="lg">Personen im Haus</span>'),
('aria-label="Mniej osób"', 'aria-label="Fewer people"', 'aria-label="Weniger Personen"'),
('aria-label="Więcej osób"', 'aria-label="More people"', 'aria-label="Mehr Personen"'),
('<span class="fs-label" id="lp">Psy lub koty</span>', '<span class="fs-label" id="lp">Dogs or cats</span>', '<span class="fs-label" id="lp">Hunde oder Katzen</span>'),
('aria-label="Mniej zwierząt"', 'aria-label="Fewer pets"', 'aria-label="Weniger Tiere"'),
('aria-label="Więcej zwierząt"', 'aria-label="More pets"', 'aria-label="Mehr Tiere"'),
('<span>Osoby ponad 10 w domu: na ile nocy?</span><small>100 zł · os. / noc</small>',
 '<span>People above 10 in the house: for how many nights?</span><small>100 zł (25 €) · person / night</small>',
 '<span>Personen über 10 im Haus: für wie viele Nächte?</span><small>100 zł (25 €) · Person / Nacht</small>'),
('aria-label="Liczba nocy dla osób ponad 10"', 'aria-label="Nights for people above 10"', 'aria-label="Nächte für Personen über 10"'),
('aria-label="Mniej nocy"', 'aria-label="Fewer nights"', 'aria-label="Weniger Nächte"'),
('aria-label="Więcej nocy"', 'aria-label="More nights"', 'aria-label="Mehr Nächte"'),
('<span class="fs-label">Dodatki</span><small style="color:var(--ink-2)">Namioty glampingowe i pole kempingowe dobierasz do wynajmu domu.</small>',
 '<span class="fs-label">Extras</span><small style="color:var(--ink-2)">Glamping tents and the camping field are added to the house rental.</small>',
 '<span class="fs-label">Extras</span><small style="color:var(--ink-2)">Glampingzelte und Zeltwiese werden zur Hausmiete dazugebucht.</small>'),
('<span class="eyebrow">Wycena orientacyjna</span>', '<span class="eyebrow">Estimated price</span>', '<span class="eyebrow">Unverbindliche Preisschätzung</span>'),
('<div class="total"><span>Razem</span>', '<div class="total"><span>Total</span>', '<div class="total"><span>Gesamt</span>'),
('id="toForm">Zapytaj o ten termin</a>', 'id="toForm">Ask about these dates</a>', 'id="toForm">Diesen Termin anfragen</a>'),
('<span class="eyebrow">Pakiet</span><h3>Magiczny weekend</h3><span class="price num">3700 zł</span>',
 '<span class="eyebrow">Package</span><h3>Magical Weekend</h3><span class="price num">3700 zł (925 €)</span>',
 '<span class="eyebrow">Paket</span><h3>Magisches Wochenende</h3><span class="price num">3700 zł (925 €)</span>'),
('<ul><li>do 12 osób, piątek – niedziela</li><li>wcześniejszy przyjazd od 14:00, późniejszy wyjazd do 14:00</li><li>balia, sprzątanie i 2 godziny sauny w cenie</li><li>przedłużenie o 1 dzień 599 zł, o 2 dni 999 zł</li><li>poza czerwcem, lipcem, sierpniem i świętami</li></ul>',
 '<ul><li>up to 12 people, Friday – Sunday</li><li>early arrival from 2 pm, late departure until 2 pm</li><li>hot tub, cleaning and 2 hours of sauna included</li><li>extra day 599 zł, two extra days 999 zł</li><li>not in June, July, August or on public holidays</li></ul>',
 '<ul><li>bis zu 12 Personen, Freitag – Sonntag</li><li>frühere Anreise ab 14:00, spätere Abreise bis 14:00</li><li>Badezuber, Endreinigung und 2 Stunden Sauna inklusive</li><li>Verlängerung um 1 Tag 599 zł, um 2 Tage 999 zł</li><li>nicht im Juni, Juli, August und an Feiertagen</li></ul>'),
('<span class="eyebrow">Pakiet</span><h3>Turnusy wakacyjne 2027</h3><span class="price num">7500 zł / 7 dni</span>',
 '<span class="eyebrow">Package</span><h3>Summer weeks 2027</h3><span class="price num">7500 zł (1875 €) / 7 days</span>',
 '<span class="eyebrow">Paket</span><h3>Sommerwochen 2027</h3><span class="price num">7500 zł (1875 €) / 7 Tage</span>'),
('<ul><li>do 10 osób, czerwiec – wrzesień</li><li>balia i sprzątanie w cenie</li><li>2 godziny sauny dziennie</li><li>3 porcje drewna</li></ul>',
 '<ul><li>up to 10 people, June – September</li><li>hot tub and cleaning included</li><li>2 hours of sauna a day</li><li>3 portions of firewood</li></ul>',
 '<ul><li>bis zu 10 Personen, Juni – September</li><li>Badezuber und Endreinigung inklusive</li><li>2 Stunden Sauna pro Tag</li><li>3 Portionen Holz</li></ul>'),
('<summary>Wszystkie dopłaty, usługi dodatkowe, prąd i kaucja</summary>',
 '<summary>All surcharges, extra services, electricity and deposit</summary>',
 '<summary>Alle Zuschläge, Zusatzleistungen, Strom und Kaution</summary>'),

# ---------- wydarzenia ----------
('<span class="eyebrow">Wydarzenia</span>', '<span class="eyebrow">Events</span>', '<span class="eyebrow">Events</span>'),
('<h2>Narnia na Wasze wydarzenie</h2>', '<h2>Narnia for your event</h2>', '<h2>Narnia für Ihr Event</h2>'),
('Mamy doświadczenie z festiwali muzycznych i zajmujemy się wszystkim od A do Z. Jesteśmy otwarci na wyzwania i odważne pomysły.',
 'We have experience with music festivals and take care of everything from A to Z. We love a challenge and bold ideas.',
 'Wir haben Erfahrung mit Musikfestivals und kümmern uns um alles von A bis Z. Wir sind offen für Herausforderungen und mutige Ideen.'),
('<h3 style="margin-top:56px">Nasze oferty</h3>', '<h3 style="margin-top:56px">Our offers</h3>', '<h3 style="margin-top:56px">Unsere Angebote</h3>'),
('<a class="btn" href="#kontakt">Zapytaj o wydarzenie</a>', '<a class="btn" href="#kontakt">Ask about an event</a>', '<a class="btn" href="#kontakt">Event anfragen</a>'),

# ---------- opinie ----------
('<span class="eyebrow">Opinie gości</span>', '<span class="eyebrow">Guest reviews</span>', '<span class="eyebrow">Gästestimmen</span>'),
('aria-label="Poprzednia opinia"', 'aria-label="Previous review"', 'aria-label="Vorherige Bewertung"'),
('aria-label="Następna opinia"', 'aria-label="Next review"', 'aria-label="Nächste Bewertung"'),
('<span class="eyebrow">Wszystkie opinie</span>', '<span class="eyebrow">All reviews</span>', '<span class="eyebrow">Alle Bewertungen</span>'),
('https://www.airbnb.pl/rooms/', 'https://www.airbnb.com/rooms/', 'https://www.airbnb.de/rooms/'),

# ---------- FAQ / kontakt ----------
('<span class="eyebrow">Dobrze wiedzieć</span><h2>Najczęstsze pytania</h2>', '<span class="eyebrow">Good to know</span><h2>Frequently asked questions</h2>', '<span class="eyebrow">Gut zu wissen</span><h2>Häufige Fragen</h2>'),
('<span class="eyebrow">Kontakt i rezerwacje</span>', '<span class="eyebrow">Contact &amp; bookings</span>', '<span class="eyebrow">Kontakt &amp; Buchung</span>'),
('<h2 style="margin-top:10px">Zarezerwuj swój czas w Narnii</h2>', '<h2 style="margin-top:10px">Book your time in Narnia</h2>', '<h2 style="margin-top:10px">Buchen Sie Ihre Zeit in Narnia</h2>'),
('Napisz przez formularz albo mailowo. Masz pomysł na wydarzenie, warsztaty czy wesele? Chętnie pomożemy.',
 'Write to us via the form or by email. Planning an event, a workshop or a wedding? We\'re happy to help. We speak English.',
 'Schreiben Sie uns über das Formular oder per E-Mail. Sie planen ein Event, einen Workshop oder eine Hochzeit? Wir helfen gerne. Wir sprechen Deutsch und Englisch.'),
('data-copy="info@narniaglamp.com">Kopiuj</button>', 'data-copy="info@narniaglamp.com">Copy</button>', 'data-copy="info@narniaglamp.com">Kopieren</button>'),
('<div class="k">Adres</div><div class="v">Krzywa 18, 66-010 Krzywa<button class="copy" data-copy="Krzywa 18, 66-010 Krzywa">Kopiuj</button>',
 '<div class="k">Address</div><div class="v">Krzywa 18, 66-010 Krzywa, Poland<button class="copy" data-copy="Krzywa 18, 66-010 Krzywa, Poland">Copy</button>',
 '<div class="k">Adresse</div><div class="v">Krzywa 18, 66-010 Krzywa, Polen<button class="copy" data-copy="Krzywa 18, 66-010 Krzywa, Polen">Kopieren</button>'),
('<div class="k">Dojazd</div>', '<div class="k">Getting here</div>', '<div class="k">Anfahrt</div>'),
('Wyznacz trasę w Mapach Google →', 'Get directions in Google Maps →', 'Route in Google Maps planen →'),
('<div class="k">Rezerwuj też przez</div>', '<div class="k">Also book via</div>', '<div class="k">Auch buchbar über</div>'),
('<div class="k">Obserwuj</div>', '<div class="k">Follow</div>', '<div class="k">Folgen</div>'),
('<h3>Zapytanie o termin</h3>', '<h3>Booking enquiry</h3>', '<h3>Terminanfrage</h3>'),
('<label for="fName">Imię i nazwisko</label>', '<label for="fName">Full name</label>', '<label for="fName">Vor- und Nachname</label>'),
('<label for="fPhone">Telefon</label>', '<label for="fPhone">Phone</label>', '<label for="fPhone">Telefon</label>'),
('<label for="fMsg">Wiadomość</label><textarea id="fMsg" placeholder="Okazja, pytania, życzenia…">',
 '<label for="fMsg">Message</label><textarea id="fMsg" placeholder="Occasion, questions, wishes…">',
 '<label for="fMsg">Nachricht</label><textarea id="fMsg" placeholder="Anlass, Fragen, Wünsche…">'),
('<button class="btn" type="submit">Wyślij zapytanie</button>', '<button class="btn" type="submit">Send enquiry</button>', '<button class="btn" type="submit">Anfrage senden</button>'),
('alt="Logo Narnia Glamp">© Narnia Glamp · Krzywa 18, 66-010 Krzywa</span>', 'alt="Narnia Glamp logo">© Narnia Glamp · Krzywa 18, 66-010 Krzywa, Poland</span>', 'alt="Logo Narnia Glamp">© Narnia Glamp · Krzywa 18, 66-010 Krzywa, Polen</span>'),
('<a href="regulamin.html">Regulamin</a> · <a href="#kontakt">Kontakt</a>', '<a href="../regulamin.html">House rules (PL)</a> · <a href="#kontakt">Contact</a>', '<a href="../regulamin.html">Hausordnung (PL)</a> · <a href="#kontakt">Kontakt</a>'),
('aria-label="Galeria zdjęć"', 'aria-label="Photo gallery"', 'aria-label="Fotogalerie"'),
('<button id="lbClose">Zamknij ✕</button>', '<button id="lbClose">Close ✕</button>', '<button id="lbClose">Schließen ✕</button>'),
('<button id="lbPrev">← Poprzednie</button><button id="lbNext">Następne →</button>', '<button id="lbPrev">← Previous</button><button id="lbNext">Next →</button>', '<button id="lbPrev">← Zurück</button><button id="lbNext">Weiter →</button>'),

# ---------- skrypt: daty i sezon ----------
("const MONTHS=['styczeń','luty','marzec','kwiecień','maj','czerwiec','lipiec','sierpień','wrzesień','październik','listopad','grudzień'];",
 "const MONTHS=['January','February','March','April','May','June','July','August','September','October','November','December'];",
 "const MONTHS=['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'];"),
("$('#seasonTxt').textContent=(isHigh(today)?'Teraz sezon wysoki: od 1300 zł za dobę':'Teraz sezon niski: od 1200 zł za dobę')+' za cały obiekt';",
 "$('#seasonTxt').textContent=(isHigh(today)?'Now high season: from 1300 zł (325 €) per night':'Now low season: from 1200 zł (300 €) per night')+' for the whole property';",
 "$('#seasonTxt').textContent=(isHigh(today)?'Jetzt Hauptsaison: ab 1300 zł (325 €) pro Nacht':'Jetzt Nebensaison: ab 1200 zł (300 €) pro Nacht')+' für das ganze Anwesen';"),
("?'high':'low'],'teraz')", "?'high':'low'],'now')", "?'high':'low'],'jetzt')"),
("'low':''],'Twój termin')", "'low':''],'your dates')", "'low':''],'Ihr Termin')"),

# ---------- skrypt: dom ----------
("{n:'Sypialnia 5-osobowa',d:'Pięć łóżek jednoosobowych.'", "{n:'Bedroom for 5',d:'Five single beds.'", "{n:'Schlafzimmer für 5',d:'Fünf Einzelbetten.'"),
("{n:'Sypialnia 2-osobowa',d:'Dwa łóżka jednoosobowe.'", "{n:'Bedroom for 2',d:'Two single beds.'", "{n:'Schlafzimmer für 2',d:'Zwei Einzelbetten.'"),
("{n:'Sypialnia rodzinna',d:'Łóżko piętrowe: dwuosobowe na dole i jednoosobowe na górze. W sam raz dla rodziny 2+1.'",
 "{n:'Family bedroom',d:'Bunk bed: a double below and a single above. Just right for a family of three.'",
 "{n:'Familienzimmer',d:'Etagenbett: unten ein Doppelbett, oben ein Einzelbett. Ideal für eine Familie mit Kind.'"),
("{n:'Salon',d:'Rozkładana sofa na 2 dodatkowe miejsca. Wyjście na taras południowy.'", "{n:'Living room',d:'Sofa bed for 2 extra people. Opens onto the south terrace.'", "{n:'Wohnzimmer',d:'Schlafsofa für 2 weitere Personen. Zugang zur Südterrasse.'"),
("{n:'Kuchnia',d:'Wszystkie podstawowe sprzęty i naczynia.'", "{n:'Kitchen',d:'All the basic appliances and dishes.'", "{n:'Küche',d:'Alle wichtigen Geräte und Geschirr.'"),
("{n:'Łazienki i toalety',d:'Przez cały rok łazienka w domu i w kancelarii. Latem dodatkowo 2 toalety na zewnątrz: w kontenerze oraz przy saunie i ognisku.'",
 "{n:'Bathrooms & toilets',d:'All year: a bathroom in the house and one in the old forestry office. In summer, 2 extra outdoor toilets: in a container and by the sauna and fire pit.'",
 "{n:'Bäder & Toiletten',d:'Ganzjährig ein Bad im Haus und eines in der alten Försterei-Kanzlei. Im Sommer zusätzlich 2 Toiletten draußen: im Container sowie an Sauna und Feuerstelle.'"),
("title=\"łóżko pojedyncze\"", "title=\"single bed\"", "title=\"Einzelbett\""),
("title=\"łóżko podwójne\"", "title=\"double bed\"", "title=\"Doppelbett\""),
("title=\"sofa rozkładana dla 2 osób\"", "title=\"sofa bed for 2\"", "title=\"Schlafsofa für 2\""),
]

# Miejsca na zewnątrz i aktywności: polskie nazwy są też kluczami do zdjęć, więc tłumaczymy całe tablice osobno.
SPOTS = {
 "en": [
  ['Barn','Party and recreation space with sound system and lights, a games lounge and a tea corner. Unheated – you can add patio heaters.'],
  ['Sauna & hot tub','Sauna and a hot tub, each for up to 8 people. Afterwards an ice-cold dip or the wooden shower.'],
  ['Shaman tipi','A place for a campfire, even in the rain. Tripod grill and sausage sticks.'],
  ['Viewing platform','Table and benches for meals with a view. Deer, herons and eagles are often seen.'],
  ['Tea terrace','Covered, overlooking the greenery and the beach. For afternoon tea.'],
  ['Grill terrace','Covered, south-facing, with tables and benches for shared meals.'],
  ['South terrace','Sunny, off the living room, right next to the hot tub and sauna.'],
  ['Glamping tents','Two tents with real beds: for 3 people (90 € / 360 zł per night) and for 4 people (120 € / 480 zł per night). Spring and summer, only as an add-on to renting the house.'],
  ['Camping field','Space for your own tents and campers, 60 zł (15 €) per person per night. Only as an add-on to renting the house.'],
  ['Fire circle','A stone fire pit with benches under a string of lights. Evenings with a guitar.'],
  ['Mini golf','A mini golf course for spring and summer.'],
  ['Archery target','Archery at a target, in spring and summer.'],
  ['Beach','Sandy, with deckchairs and benches.'],
  ['South hammock glade','Hammocks in the shade of oaks, on the sunny side.'],
  ['West hammock glade','The best spot for sunsets.'],
  ['Bar in the old stable','A cosy bar with a projector for watching sports.'],
  ['Bike shed','The bikes are waiting in the old stable.'],
  ['Volleyball court','Plus table tennis, darts and board games.'],
  ['Narnia garden','A green corner to relax in.'],
 ],
 "de": [
  ['Scheune','Party- und Freizeitraum mit Musikanlage und Licht, Spielelounge und Teeecke. Unbeheizt – Heizstrahler können dazugebucht werden.'],
  ['Sauna & Badezuber','Sauna und heißer Badezuber, jeweils für bis zu 8 Personen. Danach ein eiskaltes Bad oder die Holzdusche.'],
  ['Schamanen-Tipi','Ein Platz fürs Lagerfeuer, auch bei Regen. Dreibein mit Grillrost und Stockbrot-Spieße.'],
  ['Aussichtsplattform','Tisch und Bänke für Mahlzeiten mit Aussicht. Oft sieht man Rehe, Hirsche, Reiher und Adler.'],
  ['Teeterrasse','Überdacht, mit Blick ins Grüne und auf den Strand. Für den Nachmittagstee.'],
  ['Grillterrasse','Überdacht, nach Süden, mit Tischen und Bänken für gemeinsame Mahlzeiten.'],
  ['Südterrasse','Sonnig, direkt vom Wohnzimmer aus, gleich neben Badezuber und Sauna.'],
  ['Glampingzelte','Zwei Zelte mit echten Betten: für 3 Personen (90 € / 360 zł pro Nacht) und für 4 Personen (120 € / 480 zł pro Nacht). Im Frühling und Sommer, nur zusätzlich zur Hausmiete.'],
  ['Zeltwiese','Platz für eigene Zelte und Camper, 60 zł (15 €) pro Person und Nacht. Nur zusätzlich zur Hausmiete.'],
  ['Feuerkreis','Steinerne Feuerstelle mit Bänken unter einer Lichterkette. Abende mit Gitarre.'],
  ['Minigolf','Eine Minigolfbahn für Frühling und Sommer.'],
  ['Bogenschießen','Bogenschießen auf eine Zielscheibe, im Frühling und Sommer.'],
  ['Strand','Sandstrand mit Liegestühlen und Bänken.'],
  ['Hängemattenlichtung Süd','Hängematten im Schatten der Eichen, auf der Sonnenseite.'],
  ['Hängemattenlichtung West','Der beste Platz für Sonnenuntergänge.'],
  ['Bar im alten Stall','Gemütliche Bar mit Beamer für Sportübertragungen.'],
  ['Fahrradschuppen','Die Fahrräder warten im alten Stall.'],
  ['Volleyballfeld','Dazu Tischtennis, Darts und Brettspiele.'],
  ['Narnia-Garten','Eine grüne Ecke zum Ausruhen.'],
 ],
}
ACTS = {
 "en": [
  ['Kayaking','In places the Bóbr is almost a mountain river. We organise kayak trips.'],
  ['River next door','A few minutes\' walk to the Bóbr to cool off on hot days.'],
  ['Chill time','Shady spots among the trees and a sandy beach.'],
  ['Mushroom picking','Porcini and chanterelles in the surrounding forests. We have mushroom guides and baskets.'],
  ['Sauna','For up to 8 people all year round. Afterwards an ice-cold tub or the wooden shower.'],
  ['Hot tub','A hot soak for up to 8 under the open sky – under the stars in summer, among the frost in winter.'],
  ['Mini golf','A mini golf course for the whole group.'],
  ['Archery','A target and bows. Who hits the bullseye?'],
  ['Campfire under the stars','A circle of benches, lights and a guitar. The best evenings end here.'],
  ['Shaman tipi','A fire even in bad weather, and shade and calm in summer.'],
  ['Bikes','16 bikes in various sizes and 4 for kids. Rides to remember.'],
  ['DAG bunkers','The complex of Alfred Nobel\'s explosives factory from 1939 in Krzystkowice, over 35 km².'],
  ['Among the forests','Hundreds of hectares of forest beyond the fence and no close neighbours.'],
  ['Bar in the old stable','The match on a big projector screen at the bar in the former stable.'],
  ['Hammocks & sunsets','Two hammock glades, south and west, with a view of the sunset.'],
  ['Barn & games lounge','Table tennis, darts, retro games. On rainy days workshops, yoga and group activities.'],
  ['Walks','Forest tracks that clear your head.'],
  ['Platform','Meditation or a meal with a view of deer, herons and eagles.'],
 ],
 "de": [
  ['Kajakfahren','Der Bober hat stellenweise fast Gebirgscharakter. Wir organisieren Kajaktouren.'],
  ['Der Fluss nebenan','Ein paar Gehminuten zum Bober – zur Abkühlung an heißen Tagen.'],
  ['Chillen','Schattige Plätze zwischen den Bäumen und ein Sandstrand.'],
  ['Pilze sammeln','Steinpilze und Pfifferlinge in den Wäldern ringsum. Pilzbücher und Körbe haben wir da.'],
  ['Sauna','Für bis zu 8 Personen, das ganze Jahr. Danach ein eiskalter Zuber oder die Holzdusche.'],
  ['Badezuber','Heißes Bad für bis zu 8 Personen unter freiem Himmel – im Sommer unter Sternen, im Winter im Raureif.'],
  ['Minigolf','Eine Minigolfbahn für die ganze Gruppe.'],
  ['Bogenschießen','Zielscheibe und Bögen. Wer trifft ins Schwarze?'],
  ['Lagerfeuer unter Sternen','Ein Kreis aus Bänken, Lichter und eine Gitarre. Die schönsten Abende enden hier.'],
  ['Schamanen-Tipi','Lagerfeuer auch bei schlechtem Wetter, im Sommer Schatten und Ruhe.'],
  ['Fahrräder','16 Fahrräder in verschiedenen Größen und 4 Kinderräder. Touren, die man nicht vergisst.'],
  ['DAG-Bunker','Der Komplex der Sprengstofffabrik von Alfred Nobel von 1939 in Krzystkowice, über 35 km².'],
  ['Mitten im Wald','Hunderte Hektar Wald hinter dem Zaun und keine nahen Nachbarn.'],
  ['Bar im alten Stall','Das Spiel auf großer Beamer-Leinwand an der Bar im ehemaligen Stall.'],
  ['Hängematten & Sonnenuntergänge','Zwei Hängemattenlichtungen, Süd und West, mit Blick auf den Sonnenuntergang.'],
  ['Scheune & Spielelounge','Tischtennis, Darts, Retro-Spiele. Bei Regen Workshops, Yoga und Gruppenaktivitäten.'],
  ['Spaziergänge','Waldwege, die den Kopf frei machen.'],
  ['Plattform','Meditation oder ein Essen mit Blick auf Rehe, Reiher und Adler.'],
 ],
}

PAIRS += [
# ---------- skrypt: aktywności ----------
("const SEASON_NAME={lato:'lato',jesien:'jesień',zima:'zima',wiosna:'wiosna'};",
 "const SEASON_NAME={lato:'summer',jesien:'autumn',zima:'winter',wiosna:'spring'};",
 "const SEASON_NAME={lato:'Sommer',jesien:'Herbst',zima:'Winter',wiosna:'Frühling'};"),
("a[2].length===4?'cały rok'", "a[2].length===4?'all year'", "a[2].length===4?'ganzjährig'"),
("$('#actNow').textContent='Teraz: '+MONTHS[today.getMonth()];", "$('#actNow').textContent='Now: '+MONTHS[today.getMonth()];", "$('#actNow').textContent='Jetzt: '+MONTHS[today.getMonth()];"),

# ---------- skrypt: wyprawy ----------
("['Dzika plaża','Krótki spacer na dziką plażę nad rzeką. Piękny piasek i czysta, orzeźwiająca woda. Nasz faworyt na upały.']",
 "['Wild beach','A short walk to the wild beach by the river. Lovely sand and clean, refreshing water. Our favourite on hot days.']",
 "['Wilder Strand','Ein kurzer Spaziergang zum wilden Strand am Fluss. Schöner Sand und klares, erfrischendes Wasser. Unser Favorit an heißen Tagen.']"),
("['Leśne dukty','Krótki spacer leśnymi duktami. Idealny kierunek na szybkie jesienne grzybobranie.']",
 "['Forest tracks','A short walk along forest tracks. Perfect for a quick autumn mushroom hunt.']",
 "['Waldwege','Ein kurzer Spaziergang auf Waldwegen. Ideal für eine schnelle Pilzsuche im Herbst.']"),
("['Wieś i rzeka','Dookoła wsi i wzdłuż rzeki. Po drodze plac zabaw i dzika plaża.']",
 "['Village & river','Around the village and along the river. A playground and a wild beach on the way.']",
 "['Dorf & Fluss','Rund ums Dorf und am Fluss entlang. Unterwegs ein Spielplatz und ein wilder Strand.']"),
("['Kanał i dolina','Najpierw wzdłuż kanału, powrót nasypem wzdłuż doliny.']",
 "['Canal & valley','First along the canal, back along the embankment through the valley.']",
 "['Kanal & Tal','Erst am Kanal entlang, zurück auf dem Damm durchs Tal.']"),
("['Do dawnej fabryki amunicji DAG','Przy obiektach stoją tablice informacyjne. Trasę można skrócić o połowę, skręcając w stronę Narnii. <a href=\"https://nowogrodbobrz.pl/kombinat-dag/\" target=\"_blank\" rel=\"noopener\">Przewodnik PL/DE →</a>']",
 "['To the former DAG munitions factory','Information boards stand by the buildings. You can cut the route in half by turning back towards Narnia. <a href=\"https://nowogrodbobrz.pl/kombinat-dag/\" target=\"_blank\" rel=\"noopener\">Guide (PL/DE) →</a>']",
 "['Zur ehemaligen Munitionsfabrik DAG','An den Gebäuden stehen Infotafeln. Die Route lässt sich halbieren, wenn man Richtung Narnia abbiegt. <a href=\"https://nowogrodbobrz.pl/kombinat-dag/\" target=\"_blank\" rel=\"noopener\">Führer (PL/DE) →</a>']"),
("['Pętla na 2,5 godziny','Wzdłuż kanału, potem przez kanał do rzeki, sielskich wsi i lasu. Obowiązkowy przystanek przy ruinach średniowiecznej kaplicy w Podgórzycach. Dalej miejska plaża w Nowogrodzie Bobrzańskim: kąpiel, lody, obiad. Stamtąd 30 minut do Narnii.']",
 "['2.5-hour loop','Along the canal, then across it to the river, idyllic villages and forest. A must-stop at the ruins of the medieval chapel in Podgórzyce. Then the town beach in Nowogród Bobrzański: a swim, ice cream, lunch. From there 30 minutes back to Narnia.']",
 "['Rundtour 2,5 Stunden','Am Kanal entlang, dann über den Kanal zum Fluss, zu idyllischen Dörfern und in den Wald. Pflichtstopp an der Ruine der mittelalterlichen Kapelle in Podgórzyce. Weiter zum Stadtstrand in Nowogród Bobrzański: Baden, Eis, Mittagessen. Von dort 30 Minuten zurück nach Narnia.']"),
("['Szybka przejażdżka','Wałem wzdłuż Bobru, lasem do Łagody, powrót wzdłuż kanału.']",
 "['Quick ride','Along the Bóbr embankment, through the forest to Łagoda, back along the canal.']",
 "['Kurze Tour','Auf dem Deich am Bober entlang, durch den Wald nach Łagoda, zurück am Kanal.']"),
("tripHtml(WALKS,'P')", "tripHtml(WALKS,'W')", "tripHtml(WALKS,'F')"),

# ---------- skrypt: galeria ----------
("b.setAttribute('aria-label','Powiększ zdjęcie '+(i+1));", "b.setAttribute('aria-label','Enlarge photo '+(i+1));", "b.setAttribute('aria-label','Foto vergrößern '+(i+1));"),
("fig(GAL[i],'Zdjęcie '+(i+1)", "fig(GAL[i],'Photo '+(i+1)", "fig(GAL[i],'Foto '+(i+1)"),
("(lbFit?'Grafika ':'Zdjęcie ')", "(lbFit?'Graphic ':'Photo ')", "(lbFit?'Grafik ':'Foto ')"),

# ---------- skrypt: cennik i kalkulator ----------
("let cur='pln';", "let cur='eur';", "let cur='eur';"),
("const priceTxt=p=>p==null?'do potwierdzenia':p+' zł ('+p/EUR+' €) / noc';",
 "const priceTxt=p=>p==null?'to be confirmed':p+' zł ('+p/EUR+' €) / night';",
 "const priceTxt=p=>p==null?'auf Anfrage':p+' zł ('+p/EUR+' €) / Nacht';"),
("const pln=n=>cur==='eur'?(Math.round(n/EUR*100)/100).toLocaleString('pl-PL')+' €':n.toLocaleString('pl-PL')+' zł';",
 "const pln=n=>cur==='eur'?(Math.round(n/EUR*100)/100).toLocaleString('en-GB')+' €':n.toLocaleString('en-GB')+' zł';",
 "const pln=n=>cur==='eur'?(Math.round(n/EUR*100)/100).toLocaleString('de-DE')+' €':n.toLocaleString('de-DE')+' zł';"),
("const fmt=d=>d.toLocaleDateString('pl-PL',{day:'numeric',month:'long',year:'numeric'});",
 "const fmt=d=>d.toLocaleDateString('en-GB',{day:'numeric',month:'long',year:'numeric'});",
 "const fmt=d=>d.toLocaleDateString('de-DE',{day:'numeric',month:'long',year:'numeric'});"),
("{id:'balia',n:'Balia z drewnem',p:300,unit:'raz'", "{id:'balia',n:'Hot tub with firewood',p:300,unit:'each'", "{id:'balia',n:'Badezuber mit Holz',p:300,unit:'pro Mal'"),
("{id:'sauna',n:'Sauna',p:50,unit:'godz.'", "{id:'sauna',n:'Sauna',p:50,unit:'hour'", "{id:'sauna',n:'Sauna',p:50,unit:'Std.'"),
("{id:'ogn',n:'Drewno na ognisko',p:50,unit:'porcja'", "{id:'ogn',n:'Campfire wood',p:50,unit:'portion'", "{id:'ogn',n:'Holz fürs Lagerfeuer',p:50,unit:'Portion'"),
("{id:'early',n:'Wcześniejszy przyjazd od 14:00',p:120,unit:'jeśli możliwe'", "{id:'early',n:'Early arrival from 2 pm',p:120,unit:'if possible'", "{id:'early',n:'Frühere Anreise ab 14:00',p:120,unit:'wenn möglich'"),
("{id:'late',n:'Późniejszy wyjazd do 14:00',p:120,unit:'jeśli możliwe'", "{id:'late',n:'Late departure until 2 pm',p:120,unit:'if possible'", "{id:'late',n:'Spätere Abreise bis 14:00',p:120,unit:'wenn möglich'"),
("{id:'umb',n:'Parasol grzewczy do stodoły',p:200,unit:'z butlą 11 kg'", "{id:'umb',n:'Patio heater for the barn',p:200,unit:'with 11 kg gas bottle'", "{id:'umb',n:'Heizstrahler für die Scheune',p:200,unit:'mit 11-kg-Gasflasche'"),
("{id:'g3',n:'Namiot glampingowy na 3 osoby: liczba nocy',p:PRICES.glamp3,unit:'za noc, wiosna–lato'", "{id:'g3',n:'Glamping tent for 3: number of nights',p:PRICES.glamp3,unit:'per night, spring–summer'", "{id:'g3',n:'Glampingzelt für 3: Anzahl Nächte',p:PRICES.glamp3,unit:'pro Nacht, Frühling–Sommer'"),
("{id:'g4',n:'Namiot glampingowy na 4 osoby: liczba nocy',p:PRICES.glamp4,unit:'za noc, wiosna–lato'", "{id:'g4',n:'Glamping tent for 4: number of nights',p:PRICES.glamp4,unit:'per night, spring–summer'", "{id:'g4',n:'Glampingzelt für 4: Anzahl Nächte',p:PRICES.glamp4,unit:'pro Nacht, Frühling–Sommer'"),
("{id:'tent',n:'Pole kempingowe: liczba osób',p:60,unit:'os. / noc'", "{id:'tent',n:'Camping field: number of people',p:60,unit:'person / night'", "{id:'tent',n:'Zeltwiese: Anzahl Personen',p:60,unit:'Person / Nacht'"),
("{id:'tentN',n:'Pole kempingowe: na ile nocy'", "{id:'tentN',n:'Camping field: for how many nights'", "{id:'tentN',n:'Zeltwiese: für wie viele Nächte'"),
("aria-label=\"Mniej\">−</button>", "aria-label=\"Less\">−</button>", "aria-label=\"Weniger\">−</button>"),
("aria-label=\"Więcej\">+</button>", "aria-label=\"More\">+</button>", "aria-label=\"Mehr\">+</button>"),
("'<p class=\"warn\">Data wyjazdu musi być po dacie przyjazdu.</p>'", "'<p class=\"warn\">The departure date must be after the arrival date.</p>'", "'<p class=\"warn\">Das Abreisedatum muss nach dem Anreisedatum liegen.</p>'"),
("warn.push(`Minimalny okres najmu w tym terminie to ${minN} doby${julAug?' (latem 3 doby)':''}.`);",
 "warn.push(`The minimum stay for these dates is ${minN} nights${julAug?' (3 nights in summer)':''}.`);",
 "warn.push(`Der Mindestaufenthalt in diesem Zeitraum beträgt ${minN} Nächte${julAug?' (im Sommer 3 Nächte)':''}.`);"),
("warn.push('Od października do marca w domu nocuje do 10 osób.');", "warn.push('From October to March up to 10 people can sleep in the house.');", "warn.push('Von Oktober bis März übernachten bis zu 10 Personen im Haus.');"),
("warn.push('Namioty glampingowe są dostępne od kwietnia do września.');", "warn.push('Glamping tents are available from April to September.');", "warn.push('Glampingzelte gibt es von April bis September.');"),
("warn.push(`Na terenie może nocować łącznie do 20 osób, a wybrano ${onSite}.`);", "warn.push(`Up to 20 people in total can stay on site; you selected ${onSite}.`);", "warn.push(`Auf dem Gelände können insgesamt bis zu 20 Personen übernachten, gewählt: ${onSite}.`);"),
("lines.push([`Noclegi: ${nights} ${nights===1?'noc':nights<5?'noce':'nocy'} (${wk} weekend./święt., ${slow} SLOW)`,sum]);",
 "lines.push([`Accommodation: ${nights} ${nights===1?'night':'nights'} (${wk} weekend/holiday, ${slow} SLOW)`,sum]);",
 "lines.push([`Übernachtung: ${nights} ${nights===1?'Nacht':'Nächte'} (${wk} Wochenende/Feiertag, ${slow} SLOW)`,sum]);"),
("lines.push([`Osoby ponad 10: ${extraG} × ${pln(100)} × ${st.xgN} ${st.xgN===1?'noc':'nocy'}`,extraG*100*st.xgN]);",
 "lines.push([`People above 10: ${extraG} × ${pln(100)} × ${st.xgN} ${st.xgN===1?'night':'nights'}`,extraG*100*st.xgN]);",
 "lines.push([`Personen über 10: ${extraG} × ${pln(100)} × ${st.xgN} ${st.xgN===1?'Nacht':'Nächte'}`,extraG*100*st.xgN]);"),
("lines.push(['Sprzątanie końcowe',400]);", "lines.push(['Final cleaning',400]);", "lines.push(['Endreinigung',400]);"),
("lines.push([`Zwierzęta: ${st.pets} × ${pln(100)}`,st.pets*100]);", "lines.push([`Pets: ${st.pets} × ${pln(100)}`,st.pets*100]);", "lines.push([`Haustiere: ${st.pets} × ${pln(100)}`,st.pets*100]);"),
("ex.push([`Balia × ${st.balia}`,st.balia*300]);", "ex.push([`Hot tub × ${st.balia}`,st.balia*300]);", "ex.push([`Badezuber × ${st.balia}`,st.balia*300]);"),
("ex.push([`Sauna ${st.sauna} godz.`,st.sauna*50]);", "ex.push([`Sauna ${st.sauna} h`,st.sauna*50]);", "ex.push([`Sauna ${st.sauna} Std.`,st.sauna*50]);"),
("ex.push([`Drewno na ognisko × ${st.ogn}`,st.ogn*50]);", "ex.push([`Campfire wood × ${st.ogn}`,st.ogn*50]);", "ex.push([`Lagerfeuerholz × ${st.ogn}`,st.ogn*50]);"),
("tbd.push(`Namiot glampingowy na ${n} os.`);else ex.push([`Namiot glampingowy na ${n} os. × ${st[k]} ${st[k]===1?'noc':'nocy'}`,p*st[k]])",
 "tbd.push(`Glamping tent for ${n}`);else ex.push([`Glamping tent for ${n} × ${st[k]} ${st[k]===1?'night':'nights'}`,p*st[k]])",
 "tbd.push(`Glampingzelt für ${n}`);else ex.push([`Glampingzelt für ${n} × ${st[k]} ${st[k]===1?'Nacht':'Nächte'}`,p*st[k]])"),
("ex.push([`Pole kempingowe: ${st.tent} os. × ${st.tentN} ${st.tentN===1?'noc':'nocy'}`,st.tent*60*st.tentN]);",
 "ex.push([`Camping field: ${st.tent} people × ${st.tentN} ${st.tentN===1?'night':'nights'}`,st.tent*60*st.tentN]);",
 "ex.push([`Zeltwiese: ${st.tent} Pers. × ${st.tentN} ${st.tentN===1?'Nacht':'Nächte'}`,st.tent*60*st.tentN]);"),
("if(st.early)ex.push(['Wcześniejszy przyjazd',120]);", "if(st.early)ex.push(['Early arrival',120]);", "if(st.early)ex.push(['Frühere Anreise',120]);"),
("if(st.late)ex.push(['Późniejszy wyjazd',120]);", "if(st.late)ex.push(['Late departure',120]);", "if(st.late)ex.push(['Spätere Abreise',120]);"),
("if(st.umb)ex.push(['Parasol grzewczy',200]);", "if(st.umb)ex.push(['Patio heater',200]);", "if(st.umb)ex.push(['Heizstrahler',200]);"),
("<span>cena do potw.</span>", "<span>price on request</span>", "<span>Preis auf Anfrage</span>"),
("$('#calcNote').textContent=`Do tego kaucja zwrotna ${pln(1000)} (przy wydarzeniach ustalana indywidualnie). Rezerwację potwierdza zadatek 50%. Prąd: 100 kWh w cenie, powyżej 0,5 ct za kWh. Ostateczną cenę potwierdzamy mailowo.`;",
 "$('#calcNote').textContent=`Plus a refundable deposit of ${pln(1000)} (set individually for events). A 50% down payment confirms the booking. Electricity: 100 kWh included, above that 0.5 ct per kWh. We confirm the final price by email.`;",
 "$('#calcNote').textContent=`Dazu eine Kaution von ${pln(1000)} (bei Events individuell). Eine Anzahlung von 50 % bestätigt die Buchung. Strom: 100 kWh inklusive, darüber 0,5 ct pro kWh. Den Endpreis bestätigen wir per E-Mail.`;"),
("packs.push({n:'Magiczny weekend'+(nights>2?` + ${nights-2} ${nights===3?'dzień':'dni'}`:'')",
 "packs.push({n:'Magical Weekend'+(nights>2?` + ${nights-2} ${nights===3?'day':'days'}`:'')",
 "packs.push({n:'Magisches Wochenende'+(nights>2?` + ${nights-2} ${nights===3?'Tag':'Tage'}`:'')"),
("packs.push({n:'Turnus wakacyjny 7 dni'", "packs.push({n:'Summer week, 7 days'", "packs.push({n:'Sommerwoche, 7 Tage'"),
("${save>0?'Taniej o '+pln(save)+' niż cena standardowa.':'Pakiet nie wychodzi taniej przy tych dodatkach.'}",
 "${save>0?pln(save)+' cheaper than the standard price.':'With these extras the package is not cheaper.'}",
 "${save>0?pln(save)+' günstiger als der Standardpreis.':'Mit diesen Extras ist das Paket nicht günstiger.'}"),
("lastQuote=`Termin: ${fmt(a)} – ${fmt(b)} (${nights} noce)\\nOsoby w domu: ${st.guests}${st.g3?` + namiot glampingowy 3 os. (${st.g3} n.)`:''}${st.g4?` + namiot glampingowy 4 os. (${st.g4} n.)`:''}${st.tent&&st.tentN?` + ${st.tent} os. na polu kempingowym (${st.tentN} n.)`:''}${st.pets?`, zwierzęta: ${st.pets}`:''}\\nDodatki: ${ex.map(e=>e[0]).concat(tbd).join(', ')||'brak'}\\nWycena orientacyjna: ${pln(total)}${packs.length?`\\nPakiet: ${packs.map(p=>p.n+' '+pln(p.p)).join('; ')}`:''}`;",
 "lastQuote=`Dates: ${fmt(a)} – ${fmt(b)} (${nights} nights)\\nPeople in the house: ${st.guests}${st.g3?` + glamping tent for 3 (${st.g3} n.)`:''}${st.g4?` + glamping tent for 4 (${st.g4} n.)`:''}${st.tent&&st.tentN?` + ${st.tent} on the camping field (${st.tentN} n.)`:''}${st.pets?`, pets: ${st.pets}`:''}\\nExtras: ${ex.map(e=>e[0]).concat(tbd).join(', ')||'none'}\\nEstimated price: ${pln(total)}${packs.length?`\\nPackage: ${packs.map(p=>p.n+' '+pln(p.p)).join('; ')}`:''}`;",
 "lastQuote=`Termin: ${fmt(a)} – ${fmt(b)} (${nights} Nächte)\\nPersonen im Haus: ${st.guests}${st.g3?` + Glampingzelt für 3 (${st.g3} N.)`:''}${st.g4?` + Glampingzelt für 4 (${st.g4} N.)`:''}${st.tent&&st.tentN?` + ${st.tent} Pers. auf der Zeltwiese (${st.tentN} N.)`:''}${st.pets?`, Haustiere: ${st.pets}`:''}\\nExtras: ${ex.map(e=>e[0]).concat(tbd).join(', ')||'keine'}\\nPreisschätzung: ${pln(total)}${packs.length?`\\nPaket: ${packs.map(p=>p.n+' '+pln(p.p)).join('; ')}`:''}`;"),

# ---------- skrypt: dopłaty ----------
("const FEES=[['Pies lub kot (za pobyt)',100],['Każda osoba ponad 10 (za noc)',100],['Pole kempingowe, własny namiot lub kamper (os./noc)',60],['Sprzątanie jednorazowe',400],['Przygotowanie balii z drewnem',300],['Sauna (godzina)',50],['Drewno na ognisko',50],['Drewno do balii',60],['Wypożyczenie kiltu do sauny',10],['Zgubiona piłka golfowa',10],['Parasol grzewczy z butlą 11 kg',200],['Wyjazd do 16:00 (jeśli możliwe)',200],['Wyjazd do 14:00 (jeśli możliwe)',120],['Przyjazd od 12:00 (jeśli możliwe)',200],['Przyjazd od 14:00 (jeśli możliwe)',120],['Brak segregacji śmieci',150],['Dodatkowe sprzątanie',200]];",
 "const FEES=[['Dog or cat (per stay)',100],['Each person above 10 (per night)',100],['Camping field, own tent or camper (person/night)',60],['One-off cleaning',400],['Hot tub preparation with firewood',300],['Sauna (per hour)',50],['Campfire wood',50],['Hot tub firewood',60],['Sauna kilt rental',10],['Lost golf ball',10],['Patio heater with 11 kg gas bottle',200],['Departure until 4 pm (if possible)',200],['Departure until 2 pm (if possible)',120],['Arrival from 12 noon (if possible)',200],['Arrival from 2 pm (if possible)',120],['Waste not sorted',150],['Extra cleaning',200]];",
 "const FEES=[['Hund oder Katze (pro Aufenthalt)',100],['Jede Person über 10 (pro Nacht)',100],['Zeltwiese, eigenes Zelt oder Camper (Pers./Nacht)',60],['Einmalige Endreinigung',400],['Vorbereitung des Badezubers mit Holz',300],['Sauna (pro Stunde)',50],['Holz fürs Lagerfeuer',50],['Holz für den Badezuber',60],['Saunakilt leihen',10],['Verlorener Golfball',10],['Heizstrahler mit 11-kg-Gasflasche',200],['Abreise bis 16:00 (wenn möglich)',200],['Abreise bis 14:00 (wenn möglich)',120],['Anreise ab 12:00 (wenn möglich)',200],['Anreise ab 14:00 (wenn möglich)',120],['Müll nicht getrennt',150],['Zusätzliche Reinigung',200]];"),
("FEES.push(['Namiot glampingowy na 3 osoby (noc)',360],['Namiot glampingowy na 4 osoby (noc)',480],['Prąd: 100 kWh w cenie, każda kolejna kWh','0,5 ct'],['Ładowanie samochodu elektrycznego (kWh)','0,5 ct'],['Kaucja zwrotna (wydarzenia: wycena indywidualna)',1000]);",
 "FEES.push(['Glamping tent for 3 (night)',360],['Glamping tent for 4 (night)',480],['Electricity: 100 kWh included, each further kWh','0.5 ct'],['Electric car charging (kWh)','0.5 ct'],['Refundable deposit (events: individual quote)',1000]);",
 "FEES.push(['Glampingzelt für 3 (Nacht)',360],['Glampingzelt für 4 (Nacht)',480],['Strom: 100 kWh inklusive, jede weitere kWh','0,5 ct'],['Laden eines E-Autos (kWh)','0,5 ct'],['Kaution (Events: individuell)',1000]);"),
("f[1]+' zł ('+(f[1]/4).toLocaleString('pl-PL')+' €)'", "f[1]+' zł ('+(f[1]/4).toLocaleString('en-GB')+' €)'", "f[1]+' zł ('+(f[1]/4).toLocaleString('de-DE')+' €)'"),

# ---------- skrypt: wydarzenia ----------
("'Event firmowy',['kompleksowa obsługa eventu','oświetlenie i nagłośnienie','catering','animacje, atrakcje i gry zespołowe','namioty, stoły, krzesła, meble eventowe','relacja foto/video']",
 "'Company event',['full event management','lighting and sound','catering','entertainment, activities and team games','tents, tables, chairs, event furniture','photo/video coverage']",
 "'Firmenevent',['Rundum-Organisation','Licht und Ton','Catering','Animation, Attraktionen und Teamspiele','Zelte, Tische, Stühle, Eventmöbel','Foto-/Videobegleitung']"),
("'Warsztaty',['przestrzeń w stodole lub pod namiotami','pomoce dydaktyczne (tablice, projektor)','meble eventowe i oświetlenie terenu','catering','rowery dla uczestników']",
 "'Workshops',['space in the barn or under marquees','teaching aids (boards, projector)','event furniture and site lighting','catering','bikes for participants']",
 "'Workshops',['Raum in der Scheune oder unter Zelten','Hilfsmittel (Tafeln, Beamer)','Eventmöbel und Geländebeleuchtung','Catering','Fahrräder für die Teilnehmenden']"),
("'Wesela',['kompleksowa obsługa','nagłośnienie, oświetlenie terenu, dekoracje','DJ, orkiestra, prowadzenie','namioty, meble eventowe, strefy chill','catering i relacja foto/video','logistyka']",
 "'Weddings',['full service','sound, site lighting, decorations','DJ, band, host','marquees, event furniture, chill zones','catering and photo/video coverage','logistics']",
 "'Hochzeiten',['Rundum-Service','Ton, Geländebeleuchtung, Deko','DJ, Band, Moderation','Zelte, Eventmöbel, Chill-Bereiche','Catering und Foto-/Video','Logistik']"),
("'Festiwalowe urodziny',['kompleksowa obsługa, od A do Z','nagłośnienie, oświetlenie terenu i scen','lineup','pole namiotowe','obsługa sanitarna i techniczna']",
 "'Festival-style birthdays',['full service from A to Z','sound, site and stage lighting','line-up','camping field','sanitary and technical support']",
 "'Geburtstag im Festival-Stil',['Rundum-Service von A bis Z','Ton, Gelände- und Bühnenlicht','Line-up','Zeltplatz','Sanitär- und Technikservice']"),
("b.setAttribute('aria-label','Powiększ grafikę oferty '+(i+1));", "b.setAttribute('aria-label','Enlarge offer graphic '+(i+1));", "b.setAttribute('aria-label','Angebotsgrafik vergrößern '+(i+1));"),
("fig(p,'Oferta '+(i+1)", "fig(p,'Offer '+(i+1)", "fig(p,'Angebot '+(i+1)"),

# ---------- skrypt: opinie ----------
("const REV=[['Przepiękne miejsce na wypoczynek.','Ewa M., lipiec 2026'],['Einmalig toll.','Sylke S., sierpień 2026'],['Drugi pobyt i znów było świetnie: przestrzeń, spokój i mnóstwo atrakcji.','P. B., lipiec 2026 (tłum. z niemieckiego)']];",
 "const REV=[['A beautiful place to relax.','Ewa M., July 2026 (translated from Polish)'],['Einmalig toll.','Sylke S., August 2026'],['Our second stay and it was great again: space, peace and lots to do.','P. B., July 2026 (translated from German)']];",
 "const REV=[['Ein wunderschöner Ort zum Erholen.','Ewa M., Juli 2026 (aus dem Polnischen)'],['Einmalig toll.','Sylke S., August 2026'],['Zweiter Aufenthalt und wieder großartig: Weite, Ruhe und jede Menge zu erleben.','P. B., Juli 2026']];"),

# ---------- skrypt: FAQ ----------
("['Jaki jest minimalny okres najmu?','2 doby, a latem (w lipcu i sierpniu) 3 doby.']",
 "['What is the minimum stay?','2 nights; in summer (July and August) 3 nights.']",
 "['Wie lange ist der Mindestaufenthalt?','2 Nächte, im Sommer (Juli und August) 3 Nächte.']"),
("['O której zameldowanie i wymeldowanie?','Przyjazd od 16:00, wyjazd do 12:00. Zameldowanie jest samodzielne, na kody dostępu. Wcześniejszy przyjazd lub późniejszy wyjazd za dopłatą, jeśli termin pozwala.']",
 "['What are the check-in and check-out times?','Arrival from 4 pm, departure by 12 noon. Check-in is self-service with access codes. Early arrival or late departure for a surcharge, if the calendar allows.']",
 "['Wann sind Check-in und Check-out?','Anreise ab 16:00, Abreise bis 12:00. Der Check-in erfolgt selbstständig mit Zugangscodes. Frühere Anreise oder spätere Abreise gegen Aufpreis, wenn der Kalender es zulässt.']"),
("['Jak zarezerwować?','Przez formularz, mailowo, telefonicznie albo przez portale (Slowhop, Airbnb, AlohaCamp). Rezerwację potwierdza zadatek 50% wpłacony w ciągu 3 dni.']",
 "['How do I book?','Via the form, by email or phone, or through Slowhop, Airbnb or AlohaCamp. A 50% down payment within 3 days confirms the booking.']",
 "['Wie kann ich buchen?','Über das Formular, per E-Mail oder Telefon oder über Slowhop, Airbnb oder AlohaCamp. Eine Anzahlung von 50 % innerhalb von 3 Tagen bestätigt die Buchung.']"),
("['Kiedy płacę resztę i ile wynosi kaucja?','Resztę kwoty i kaucję 1000 zł wpłacacie 7 dni przed przyjazdem. Kaucja wraca w ciągu 7 dni po wyjeździe.']",
 "['When do I pay the rest and how much is the deposit?','The balance and the 1000 zł (250 €) deposit are due 7 days before arrival. The deposit is returned within 7 days after departure.']",
 "['Wann zahle ich den Rest und wie hoch ist die Kaution?','Restbetrag und Kaution von 1000 zł (250 €) sind 7 Tage vor der Anreise fällig. Die Kaution kommt innerhalb von 7 Tagen nach der Abreise zurück.']"),
("['Ile osób może przyjechać?','Wiosną i latem w domu śpi do 12 osób (poza sezonem do 10), a w dwóch namiotach glampingowych kolejne 7. Jest też pole kempingowe. Namioty i pole są dostępne wyłącznie jako rozszerzenie wynajmu domu. Na terenie może przebywać łącznie do 20 osób. Cena domu obejmuje 10 osób. Dzieci do 4 lat gratis.']",
 "['How many people can come?','In spring and summer up to 12 people sleep in the house (10 off-season), plus 7 more in two glamping tents. There is also a camping field. Tents and the field are only available as an add-on to renting the house. Up to 20 people in total can stay on site. The house price covers 10 people. Children up to 4 stay free.']",
 "['Wie viele Personen können kommen?','Im Frühling und Sommer schlafen bis zu 12 Personen im Haus (außerhalb der Saison 10), dazu 7 weitere in zwei Glampingzelten. Außerdem gibt es eine Zeltwiese. Zelte und Zeltwiese gibt es nur zusätzlich zur Hausmiete. Insgesamt dürfen bis zu 20 Personen auf dem Gelände sein. Der Hauspreis gilt für 10 Personen. Kinder bis 4 Jahre kostenlos.']"),
("['Czy mogę przyjechać z psem?','Tak, pobyt psa lub kota kosztuje 100 zł.']",
 "['Can I bring my dog?','Yes, a dog or cat costs 100 zł (25 €) per stay.']",
 "['Darf ich meinen Hund mitbringen?','Ja, ein Hund oder eine Katze kostet 100 zł (25 €) pro Aufenthalt.']"),
("['Czy można zorganizować imprezę lub wesele?','Tak, ale wydarzenia powyżej 20 osób wymagają osobnej umowy. Napiszcie, przygotujemy ofertę: wesela, firmówki, warsztaty, urodziny w stylu festiwalu.']",
 "['Can we hold a party or a wedding?','Yes, but events above 20 people need a separate agreement. Write to us and we\\'ll prepare an offer: weddings, company events, workshops, festival-style birthdays.']",
 "['Kann man eine Feier oder Hochzeit veranstalten?','Ja, Events mit mehr als 20 Personen brauchen jedoch einen eigenen Vertrag. Schreiben Sie uns, wir erstellen ein Angebot: Hochzeiten, Firmenevents, Workshops, Geburtstage im Festival-Stil.']"),
("['Cisza nocna?','Od 22:00 do 7:00. Głośna muzyka w stodole do 22:00.']",
 "['Quiet hours?','From 10 pm to 7 am. Loud music in the barn until 10 pm.']",
 "['Nachtruhe?','Von 22:00 bis 7:00. Laute Musik in der Scheune bis 22:00.']"),
("['Gdzie są pełne zasady?','W <a href=\"regulamin.html\">regulaminie obiektu</a>.']",
 "['Where are the full rules?','In the <a href=\"../regulamin.html\">house rules</a> (in Polish; ask us for the English version).']",
 "['Wo finde ich die vollständigen Regeln?','In der <a href=\"../regulamin.html\">Hausordnung</a> (auf Polnisch; die deutsche Fassung schicken wir Ihnen gern).']"),

# ---------- skrypt: kopiowanie i formularz ----------
("b.textContent='Skopiowano';setTimeout(()=>b.textContent='Kopiuj',1600)", "b.textContent='Copied';setTimeout(()=>b.textContent='Copy',1600)", "b.textContent='Kopiert';setTimeout(()=>b.textContent='Kopieren',1600)"),
("err.textContent='Podaj imię i poprawny adres e-mail, żebyśmy mogli odpisać.'", "err.textContent='Please enter your name and a valid email address so we can reply.'", "err.textContent='Bitte geben Sie Ihren Namen und eine gültige E-Mail-Adresse an, damit wir antworten können.'"),
("const body=`${lastQuote}\\n\\nOd: ${name}\\nE-mail: ${email}\\nTelefon: ${$('#fPhone').value.trim()||'–'}\\n\\n${$('#fMsg').value.trim()}`;",
 "const body=`[EN] ${lastQuote}\\n\\nOd: ${name}\\nE-mail: ${email}\\nTelefon: ${$('#fPhone').value.trim()||'–'}\\n\\n${$('#fMsg').value.trim()}`;",
 "const body=`[DE] ${lastQuote}\\n\\nOd: ${name}\\nE-mail: ${email}\\nTelefon: ${$('#fPhone').value.trim()||'–'}\\n\\n${$('#fMsg').value.trim()}`;"),
("subject:'Zapytanie o termin – Narnia'", "subject:'Zapytanie o termin (EN) – Narnia'", "subject:'Zapytanie o termin (DE) – Narnia'"),
("'<p><strong>Dziękujemy!</strong> Zapytanie dotarło, odpiszemy na podany e-mail.</p>'", "'<p><strong>Thank you!</strong> Your enquiry has arrived – we will reply by email.</p>'", "'<p><strong>Vielen Dank!</strong> Ihre Anfrage ist angekommen – wir antworten per E-Mail.</p>'"),
("err.textContent='Nie udało się wysłać wiadomości. Spróbuj ponownie albo napisz na info@narniaglamp.com.'", "err.textContent='The message could not be sent. Please try again or write to info@narniaglamp.com.'", "err.textContent='Die Nachricht konnte nicht gesendet werden. Bitte erneut versuchen oder an info@narniaglamp.com schreiben.'"),
("'<p><strong>Podgląd strony:</strong> formularz jeszcze nie wysyła wiadomości. Na gotowej stronie trafi ona prosto na info@narniaglamp.com. Tak będzie wyglądać:</p><pre></pre>'",
 "'<p><strong>Preview:</strong> the form does not send messages yet. Your message would look like this:</p><pre></pre>'",
 "'<p><strong>Vorschau:</strong> Das Formular versendet noch keine Nachrichten. So würde Ihre Nachricht aussehen:</p><pre></pre>'"),
]

# Przełącznik języka (wstawiany do wszystkich trzech wersji) i ścieżki zasobów dla /en/ i /de/
def switcher(cur):
    def a(code, href):
        on = ' aria-current="true"' if code == cur else ''
        return f'<a href="{href}" hreflang="{code}" lang="{code}"{on}>{code.upper()}</a>'
    root = "" if cur == "pl" else "../"
    return ('<nav class="langsw" aria-label="Język / Language / Sprache">'
            + a("pl", root or "./") + a("en", root + "en/") + a("de", root + "de/") + '</nav>')

SW_CSS = (".nav a,.top .btn{white-space:nowrap}"
          ".ig-top span{display:none}.ig-top{padding:8px 10px}"
          "@media (max-width:1200px){.nav{display:none;position:absolute;left:0;right:0;top:64px;flex-direction:column;background:var(--bg);border-bottom:1px solid var(--line);padding:8px max(16px,env(safe-area-inset-right,0px)) 16px max(16px,env(safe-area-inset-left,0px))}.nav.open{display:flex}.menu-btn{display:block;margin-left:0}.ig-top{order:0;margin-left:auto;padding:8px 10px}}"
          ".langsw{order:2;display:flex;gap:2px;border:1px solid var(--line);border-radius:999px;padding:2px}"
          ".langsw a{font:600 .78rem var(--mono);letter-spacing:.06em;text-decoration:none;padding:5px 8px;border-radius:999px;color:var(--ink-2)}"
          ".langsw a[aria-current]{background:var(--ink);color:var(--bg)}"
          "@media (max-width:1200px){.langsw{margin-left:auto;order:0}.ig-top{margin-left:8px}}"
          "@media (max-width:480px){.top .wrap{gap:8px}.ig-top{display:none}.langsw a{padding:5px 6px}}")
HREFLANG = ('<link rel="alternate" hreflang="pl" href="https://narniaglamp.com/">'
            '<link rel="alternate" hreflang="en" href="https://narniaglamp.com/en/">'
            '<link rel="alternate" hreflang="de" href="https://narniaglamp.com/de/">'
            '<link rel="alternate" hreflang="x-default" href="https://narniaglamp.com/">')

def add_switcher(html, cur):
    if 'class="langsw"' in html:  # już jest — odśwież
        html = re.sub(r'<nav class="langsw".*?</nav>', switcher(cur), html, flags=re.S)
    else:
        html = html.replace('<button class="menu-btn"', switcher(cur) + '\n    <button class="menu-btn"', 1)
    if ".langsw{" in html:
        html = re.sub(r"(\.nav a,\.top \.btn\{white-space:nowrap\}[^\n]*|\.langsw\{[^\n]*)\n", lambda m: SW_CSS + "\n", html, count=1)
    else:
        html = html.replace("</style>", SW_CSS + "\n</style>", 1)
    if 'hreflang="x-default"' not in html:
        html = html.replace("<title>", HREFLANG + "\n<title>", 1)
    return html

def array_block(src, name):
    m = re.search(r"const %s=\[\n(.*?)\n\];" % name, src, re.S)
    return m

def replace_array_texts(html, name, translated):
    """Podmienia teksty w tablicy SPOTS/ACTS, zostawiając polskie nazwy jako klucze zdjęć."""
    m = array_block(html, name)
    rows = re.findall(r"  \['(.*?)','(.*?)'(,\[.*?\])?\]", m.group(1))
    assert len(rows) == len(translated), (name, len(rows), len(translated))
    out = []
    for (pl, _, seasons), (t_name, t_desc) in zip(rows, translated):
        esc = lambda s: s.replace("\\", "\\\\").replace("'", "\\'")
        out.append(f"  ['{esc(t_name)}','{esc(t_desc)}'{seasons},'{pl}']")
    return html[:m.start(1)] + ",\n".join(out) + html[m.end(1):]

def build(lang):
    src = (ROOT / "index.html").read_text(encoding="utf8")
    html = src
    missing = []
    for pl, en, de in sorted(PAIRS, key=lambda p: -len(p[0])):
        if pl not in html:
            missing.append(pl[:90])
            continue
        html = html.replace(pl, en if lang == "en" else de)
    # tablice z kluczem zdjęcia na 4. pozycji (polska nazwa)
    html = replace_array_texts(html, "SPOTS", SPOTS[lang])
    html = replace_array_texts(html, "ACTS", ACTS[lang])
    html = html.replace("${fig(SPOT_IMG[s[0]],s[0],640,400)}", "${fig(SPOT_IMG[s[2]],s[0],640,400)}")
    html = html.replace("${fig(ACT_IMG[a[0]],a[0],560,420)}", "${fig(ACT_IMG[a[3]],a[0],560,420)}")
    # język dokumentu, ścieżki zasobów, logotypy jako pliki
    html = html.replace('<html lang="pl">', f'<html lang="{lang}">', 1)
    html = html.replace('<link rel="icon" href="logo-narnia.png">', '<link rel="icon" href="../logo-narnia.png">')
    html = html.replace('content="img/', 'content="https://narniaglamp.com/img/')
    html = html.replace("const LOCAL_IMG='img/';", "const LOCAL_IMG='../img/';")
    html = html.replace("img.src=own?id:", "img.src=own?'../'+id:")
    logos = {}
    def to_file(m):
        data = base64.b64decode(m.group(2))
        name = "assets/logo-%d.png" % len(data)
        logos[name] = data
        return f'{m.group(1)}="../{name}"'
    html = re.sub(r'(src)="data:image/png;base64,([A-Za-z0-9+/=]+)"', to_file, html)
    for name, data in logos.items():
        p = ROOT / name; p.parent.mkdir(exist_ok=True)
        if not p.exists() or p.read_bytes() != data: p.write_bytes(data)
    html = add_switcher(html, lang)
    # dłuższe pozycje menu po angielsku i niemiecku: bez przycisku „Sprawdź cenę” w nagłówku (jest w sekcji powitalnej)
    html = html.replace("</style>", ".top .wrap>.btn{display:none}\n</style>", 1)
    out = ROOT / lang / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf8")
    # kontrola: polskie znaki w widocznych tekstach (poza nazwami własnymi)
    allowed = ["Bóbr", "Łagod", "Podgórzyc", "Nowogród", "Bobrzański", "Krzywa", "Wiedza", "Justyna", "Rafał", "Pieczyńscy",
               "aria-label=\"Język", "Ewa M.", "Ś", "lato", "jesień", "jesien", "SEASON_OF", "MONTHS", "SPOT_IMG", "ACT_IMG",
               "Stodoła", "Szamańskie", "Plaża", "Rowerownia", "Tarcza łucznicza", "Bar w starej stajni", "Krąg ogniskowy",
               "Taras południowy", "Spływy kajakowe", "Rzeka tuż obok", "Grzybobranie", "Wśród lasów", "Stodoła i salon gier",
               "Ognisko pod gwiazdami", "Łucznictwo", "Hamaki i zachody słońca", "Zapytanie o termin", "Od: ", "Telefon:",
               "Strona Narnia", "Platforma widokowa", "Sauna i balia", "Balia", "Mini golf", "Chilltime", "Rowery", "Bunkry DAG", "Spacery", "Platforma"]
    leftovers = []
    text = re.sub(r"<style>.*?</style>", "", html, flags=re.S)
    for line in text.splitlines():
        if re.search(r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]", line) and not any(a in line for a in allowed):
            leftovers.append(line.strip()[:140])
    return missing, leftovers

def main():
    pl = (ROOT / "index.html").read_text(encoding="utf8")
    pl2 = add_switcher(pl, "pl")
    if pl2 != pl:
        (ROOT / "index.html").write_text(pl2, encoding="utf8")
    ok = True
    for lang in LANGS:
        missing, leftovers = build(lang)
        print(f"[{lang}] gotowe: {lang}/index.html")
        for m in missing: print(f"  ! nie znaleziono w index.html: {m}"); ok = False
        for l in leftovers: print(f"  ? polski tekst: {l}")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
