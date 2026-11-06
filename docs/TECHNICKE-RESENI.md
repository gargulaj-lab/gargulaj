# Od papírové evidence k webové aplikaci

Projekt propojuje osobní evidenci jízd s grafem železniční sítě. Server v Pythonu poskytuje API, SQLite ukládá uživatele a jejich jízdy a Leaflet zobrazuje výsledky v prohlížeči.

## Výpočet trasy

Soubor app/railway.py implementuje Dijkstrův algoritmus s prioritní frontou heapq. Stanice se vyhledá podle názvu a přiřazeného rail_node. Výsledkem jsou uzly, identifikátory hran a součet délek. Průjezdní body rozdělují cestu na dílčí trasy, jejichž výsledky se spojují.

Algoritmus vybírá nejkratší cestu podle délky hran. Neověřuje jízdní řád, provozní dostupnost ani dopravní předpisy. Duplicitní názvy stanic se zatím řeší výběrem prvního záznamu.

## Proč ukládat hrany

Při opakování pětikilometrové cesty dvakrát má uživatel 10 km jízd, ale 5 km unikátní sítě. U každé jízdy se proto ukládají také identifikátory hran. Pro unikátní vzdálenost se vytvoří jejich množina a každá délka se započítá jednou.

API pro projetou síť přidává počet jízd a první a poslední datum pro každou hranu. Integrační kontrola tento rozdíl ověřuje na syntetické síti; nejde o ověření správnosti skutečné české železniční sítě.

## Rozpracovaná témata

Souběžné koleje mohou představovat různé hrany stejné tratě. Jejich sjednocení do logické sítě ovlivňuje unikátní kilometry. Nahraný archiv obsahoval experimenty zaměřené na oblast Kolína; nejsou zde vydávány za dokončenou součást aplikace. Pracovní skripty, starší server a generované výstupy zůstaly v původním archivu.

## Rozsah přípravy repozitáře

Z nahraného projektu pochází server, databázová vrstva, směrovací algoritmus a tři HTML šablony. Pro přenosné spuštění byly přidány nastavitelné cesty, závislosti, syntetická data a integrační kontrola. Osobní databáze ani odvozené velké mapové soubory nejsou součástí této verze.

## Provozní stav

Jde o lokální vývojovou aplikaci. Před veřejným provozem je nutné prověřit zejména ochranu proti CSRF, validaci dat, chybové HTTP odpovědi, omezení přihlašovacích pokusů a konfiguraci relací a HTTPS. Pouhé spuštění lokální ukázky toto ověření nenahrazuje.
