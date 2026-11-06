# Moje železnice 🚆

Webová aplikace pro evidenci projetých železničních tratí, zobrazení jízd v mapě a sledování kilometrů.

Projekt vychází z mého koníčku projíždění železničních tratí. Původní papírovou evidenci převádím do aplikace, která propojuje záznamy jízd s mapou železniční sítě. Při vývoji využívám zkušenosti strojvedoucího a rozvíjím znalosti programování, databází a geografických dat.

**Stav: projekt v aktivním vývoji.** Vyhledávání tras a výpočty závisejí na kvalitě a propojení použité železniční sítě.

## Funkce

- Registrace a přihlášení uživatele.
- Vyhledávání stanic a tras včetně průjezdních bodů.
- Zobrazení železniční sítě a tras v interaktivní mapě.
- Uložení jízdy s datem, výchozí a cílovou stanicí.
- Historie jízd a odstranění vlastního záznamu.
- Měsíční, roční a celkový součet kilometrů.
- Výpočet délky unikátně projetých úseků podle hran železničního grafu.

## Jak aplikace pracuje

1. Uživatel vybere výchozí a cílovou stanici, případně průjezdné body.
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
- Dokumentaci instalace a přípravy dat doplním podle ověřeného postupu pro zveřejněnou verzi.

## Autor a způsob vývoje

Josef Gargula — strojvedoucí s technickým vzděláním v elektrotechnice a počítačových systémech, který se rozvíjí v IT.

Projekt vzniká s podporou AI při návrhu řešení, tvorbě a úpravách kódu a hledání chyb. Znalost železničního prostředí využívám při určování potřeb aplikace a ověřování výsledků na konkrétních trasách.

Projekt mi pomáhá rozvíjet dovednosti využitelné i mimo železnici: práci s webovým rozhraním, API, databází, geografickými daty a ověřováním správnosti výsledků.

## Mapová data

Mapová data © přispěvatelé [OpenStreetMap](https://www.openstreetmap.org/copyright). Při distribuci odvozených dat je potřeba zohlednit podmínky jejich zdroje.
