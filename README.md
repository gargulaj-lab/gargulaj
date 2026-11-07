# Moje železnice 🚆

Webová aplikace pro evidenci projetých železničních tratí, zobrazení jízd v mapě a sledování kilometrů.

Projekt vychází z mého koníčku projíždění železničních tratí. Původní papírovou evidenci převádím do aplikace, která propojuje záznamy jízd s mapou železniční sítě. Při vývoji využívám zkušenosti strojvedoucího a rozvíjím znalosti programování, databází a geografických dat.

**Stav: projekt v aktivním vývoji.** Vyhledávání tras a výpočty závisejí na kvalitě a propojení použité železniční sítě.

## Vyzkoušení lokálně

Repozitář obsahuje zdrojový kód a malou **syntetickou síť**, která umožňuje vyzkoušet aplikaci bez původních dat. Stanice Demo Západ, Demo Střed a Demo Východ, jejich geometrie i vzdálenosti jsou smyšlené. Úplná železniční síť není součástí této ukázky.

Ověřeno s Pythonem 3.12.

```bash
git clone https://github.com/gargulaj-lab/gargulaj.git
cd gargulaj
python -m venv .venv
```

Aktivuj prostředí:

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- Linux/macOS: `source .venv/bin/activate`

Potom ve složce projektu spusť:

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1
```

Otevři http://127.0.0.1:8000, zaregistruj vlastní zkušební účet a vyhledej trasu **Demo Západ → Demo Východ**. Volitelně přidej průjezdní bod Demo Střed. Ulož stejnou pětikilometrovou cestu dvakrát: celkem bude 10 km, unikátně 5 km. Databáze vznikne automaticky; žádné uživatelské účty nejsou předvyplněné.

Mapový podklad a Leaflet se načítají z internetu. Směrování a evidence používají místní data. Jde o lokální vývojovou ukázku; konfigurace dosud není připravená pro veřejný provoz.

Pro použití skutečné sítě nastav cesty ke svým souborům podle [návodu k železničním datům](docs/DATA.md#vlastní-železniční-síť).

## Kontrola funkčnosti

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Integrační kontrola používá dočasnou databázi. Ověřuje registraci, přihlášení, trasu přes průjezdní bod, ukládání opakovaných jízd, unikátní kilometry, oddělení účtů a odstranění jízd. Správnost úplné železniční sítě tím ověřena není.

## Struktura a dokumentace

| Cesta | Obsah |
| --- | --- |
| app/main.py | Webové stránky a API |
| app/railway.py | Vyhledání stanic a Dijkstrův algoritmus |
| app/database.py | SQLite schéma a připojení |
| templates/ | Přihlášení, registrace a mapa s evidencí |
| data/demo/ | Syntetický graf a stanice |
| static/ | Ukázková mapová vrstva |
| tests/ | Integrační kontrola |
| [docs/DATA.md](docs/DATA.md) | Datový formát a připojení vlastní sítě |
| [docs/TECHNICKE-RESENI.md](docs/TECHNICKE-RESENI.md) | Technické řešení a omezení |

Nastavitelné cesty: `RAIL_GRAPH_FILE`, `STATION_GRAPH_FILE`, `RAIL_STATIC_DIR` a `DATABASE_FILE`. Pro relace lze nastavit `SESSION_SECRET`; soubor `.env` aplikace automaticky nenačítá.

## Funkce

- Registrace a přihlášení uživatele.
- Vyhledávání stanic a tras včetně průjezdních bodů.
- Zobrazení železniční sítě a tras v interaktivní mapě.
- Uložení jízdy s datem, výchozí a cílovou stanicí.
- Historie jízd a odstranění vlastního záznamu.
- Měsíční, roční a celkový součet kilometrů.
- Výpočet délky unikátně projetých úseků podle hran železničního grafu.

## Jak aplikace pracuje

1. Uživatel vybere výchozí a cílovou stanici, případně průjezdní body.
2. Server vyhledá trasu v železničním grafu a vrátí délku, souřadnice a identifikátory hran.
3. Aplikace zobrazí trasu v mapě.
4. Při uložení server trasu znovu vypočítá a uloží ji k přihlášenému uživateli.
5. Statistiky se sestavují z uložených jízd a z množiny unikátních hran.

## Technologie

| Část | Použité technologie |
| --- | --- |
| Server a API | Python, FastAPI, Pydantic |
| Databáze | SQLite |
| Šablony | Jinja2 |
| Uživatelské rozhraní | HTML, CSS, JavaScript |
| Mapové zobrazení | Leaflet, OpenStreetMap, GeoJSON |
| Přihlášení | Session middleware, hashování hesel pomocí pwdlib |

## Technická témata

**Vyhledávání v železniční síti.** Trasa je složena z navazujících hran grafu. Pro správný výsledek je důležité propojení sítě, přiřazení stanic a správné délky úseků.

**Celkové a unikátní kilometry.** Celková vzdálenost zahrnuje opakované jízdy. Unikátní vzdálenost počítá každou použitou hranu pouze jednou. Výsledek proto závisí na tom, jak graf zachází se souběžnými kolejemi; nejde automaticky o délku unikátních tratí v provozním smyslu.

**Propojení mapy a databáze.** U jízdy se ukládají stanice, datum, vzdálenost, souřadnice a identifikátory hran. Záznamy jsou přiřazeny konkrétnímu uživateli.

## Současná omezení a další vývoj

- Dále ověřuji propojení železniční sítě a výsledky trasování.
- Rozpracovaným tématem je sjednocování souběžných kolejí do logické sítě.
- Přesnost kilometrů závisí na zdrojových datech a podobě grafu.
- Úplný graf skutečné železniční sítě není přiložen; lokální ukázka používá syntetická data.

## Autor a způsob vývoje

Josef Gargula — strojvedoucí s technickým vzděláním v elektrotechnice a počítačových systémech, který se rozvíjí v IT.

Projekt vzniká s podporou AI při návrhu řešení, tvorbě a úpravách kódu a hledání chyb. Znalost železničního prostředí využívám při určování potřeb aplikace a ověřování výsledků na konkrétních trasách.

Projekt mi pomáhá rozvíjet dovednosti využitelné i mimo železnici: práci s webovým rozhraním, API, databází, geografickými daty a ověřováním správnosti výsledků.

## Mapová data

Mapová data © přispěvatelé [OpenStreetMap](https://www.openstreetmap.org/copyright). Při distribuci odvozených dat je potřeba zohlednit podmínky jejich zdroje.

