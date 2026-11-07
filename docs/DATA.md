# Železniční data

## Přiložená ukázka

Výchozí konfigurace používá tři smyšlené stanice Demo Západ, Demo Střed a Demo Východ a dvě hrany dlouhé 2 a 3 km. Geometrie, názvy ani délky nepopisují skutečnou trať. Data slouží pouze k vyzkoušení aplikace a integračních kontrol. Byla vytvořena pro tuto prezentaci; nejsou převzata z OSM.

## Vlastní železniční síť

Aplikace umí načíst dodané soubory `rail_graph.json` a `station_graph.json` z místního disku. Pro zobrazení sítě použij složku `static` z původního archivu projektu, která obsahuje `railway_network_multi.geojson`. Úplné datové soubory se uchovávají odděleně od zdrojového kódu.

Ve Windows PowerShell nastav cesty podle skutečného umístění souborů a spusť aplikaci ze složky repozitáře. Pro skutečnou síť použij samostatnou databázi jízd.

```powershell
$env:RAIL_GRAPH_FILE = 'C:\OSM\HRANICE\rail_graph.json'
$env:STATION_GRAPH_FILE = 'C:\OSM\HRANICE\station_graph.json'
$env:RAIL_STATIC_DIR = 'C:\OSM\MOJE_ZELEZNICE\static'
$env:DATABASE_FILE = Join-Path (Get-Location) 'data\real-network.db'
python -m uvicorn app.main:app --reload --host 127.0.0.1
```

V Linuxu a macOS nastav stejné proměnné příkazem `export` s odpovídajícími místními cestami.

Směrovací modul načetl z dodaných souborů 563 059 uzlů, 572 389 hran a 2 782 záznamů stanic. Výpočet vrátil 42,919 km pro Praha hlavní nádraží → Beroun a 74,247 km pro Praha Masarykovo nádraží → Kolín přes Praha-Vysočany a Nymburk hlavní nádraží. Hodnoty odpovídají snímku historie jízd. Kontrola se týkala směrování na těchto dvou trasách.

## Formát

- `nodes`: pole dvojic `[zeměpisná délka, zeměpisná šířka]`.
- `edges`: pole hran `[počáteční uzel, koncový uzel, délka v km]`. Směrovací modul přijímá i objekty s klíči `start`, `end`, `length_km`.
- `adjacency`: pole seznamů sousedů, indexované číslem uzlu; soused je dvojice `[sousední uzel, index hrany]`.
- `stations`: objekt s polem `stations`; položky mají `name` a `rail_node`.

Identifikátory hran v databázi odkazují na konkrétní verzi grafu. Při změně číslování hran nepoužívej staré jízdy bez migrace. Mapová vrstva, stanice a graf musí patřit ke stejné síti.

## Co ještě doplnit pro úplnou síť

Zdroj a datum OSM výřezu, skripty vytvářející oba grafy, jejich verze a ověřené propojení s mapovou vrstvou. U OSM dat zachovej připsání autorství a odpovídající licenční podmínky: https://www.openstreetmap.org/copyright.
