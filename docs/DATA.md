# Železniční data

## Přiložená ukázka

Výchozí konfigurace používá tři smyšlené stanice Demo Západ, Demo Střed a Demo Východ a dvě hrany dlouhé 2 a 3 km. Geometrie, názvy ani délky nepopisují skutečnou trať. Data slouží pouze k vyzkoušení aplikace a integračních kontrol. Byla vytvořena pro tuto prezentaci; nejsou převzata z OSM.

## Vlastní železniční síť

V nahraném projektu nebyly soubory `rail_graph.json` a `station_graph.json`. Původní aplikace je četla z `C:\OSM\HRANICE`. Úplnou síť proto nelze z tohoto repozitáře reprodukovat bez dalších podkladů. Přiložené původní GeoJSON soubory samy o sobě nenahrazují směrovací graf.

Pro vlastní data nastav před spuštěním všechny tři proměnné:

| Proměnná | Obsah |
| --- | --- |
| RAIL_GRAPH_FILE | Absolutní cesta k rail_graph.json |
| STATION_GRAPH_FILE | Absolutní cesta ke station_graph.json |
| RAIL_STATIC_DIR | Absolutní cesta ke složce s odpovídajícím railway_network_multi.geojson |

Na Windows PowerShell použij například `$env:RAIL_GRAPH_FILE = 'C:\OSM\HRANICE\rail_graph.json'`; obdobně nastav zbývající dvě proměnné. V shellu bash použij `export RAIL_GRAPH_FILE=/absolutni/cesta/rail_graph.json`.

## Formát

- `nodes`: pole dvojic `[zeměpisná délka, zeměpisná šířka]`.
- `edges`: pole hran `[počáteční uzel, koncový uzel, délka v km]`. Směrovací modul přijímá i objekty s klíči `start`, `end`, `length_km`.
- `adjacency`: pole seznamů sousedů, indexované číslem uzlu; soused je dvojice `[sousední uzel, index hrany]`.
- `stations`: objekt s polem `stations`; položky mají `name` a `rail_node`.

Identifikátory hran v databázi odkazují na konkrétní verzi grafu. Při změně číslování hran nepoužívej staré jízdy bez migrace. Mapová vrstva, stanice a graf musí patřit ke stejné síti.

## Co ještě doplnit pro úplnou síť

Zdroj a datum OSM výřezu, skripty vytvářející oba grafy, jejich verze a ověřené propojení s mapovou vrstvou. U OSM dat zachovej připsání autorství a odpovídající licenční podmínky: https://www.openstreetmap.org/copyright.
