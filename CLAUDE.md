# Kalejdo – så fungerar sidan

Kalejdo är ett kalejdoskop i webbläsaren. Speglarna visar en tårtbit av en rund behållare
med små SVG-prylar, och bilden byggs upp av 6 eller 8 speglade tårtbitar. Samma kod körs
som webbsida och, inuti ett WebView-skal, som Android-app.

- Ägare: Dick (GitHub `skitknas-ctrl`)
- Källa: https://github.com/skitknas-ctrl/Kalejdo. Ändringar görs där och kopieras sedan ut. Redigera inte filerna direkt på servern.
- Sidan är helt statisk. Den har ingen backend, ingen databas, inget PHP, inga cookies, inga externa beroenden, inget CDN och inga typsnitt utifrån.

## Filer

```
index.html            hela appen: HTML + CSS + JavaScript i en fil
props/index.json      listan över alla prylar (kategorier -> filer); läses av index.html vid start
props/<kategori>/*.svg  prylarna, en SVG per pryl (viewBox 0 0 100 100)
tools/build_index.py  bygger om props/index.json från mapparna i props/
CLAUDE.md             den här filen
```

Kategorimapparna är: `glass`, `gems`, `shapes`, `nature`, `food`, `critters`, `things`, `electro`, `christmas`
och `evaq8`. Visningsnamn och ordning finns i `tools/build_index.py`, och en mapp kan också ha en
`_category.txt` med sitt namn.

Endast `index.html` och `props/` behövs på webbservern. `tools/` och `CLAUDE.md` ska inte
publiceras. De gör ingen skada, men behövs inte.

## Hur sidan startar

1. `index.html` hämtar `props/index.json` med `fetch()` (relativ sökväg).
2. Prylarna hämtas också med `fetch()` (relativt, `props/...svg`), görs om till bilder och ritas på `<canvas>`.
3. Användarens kalejdoskop (lager, prylar, inställningar) sparas i `localStorage` under nyckeln
   `kalejdo.v1`. Det finns ingen inloggning, och inget skickas till någon server.

Alla sökvägar är relativa. Därför fungerar sidan både i roten (`https://exempel.se/`) och i en
undermapp (`https://exempel.se/kalejdo/`) utan ändringar.

## Krav på webbservern

- **http(s), inte file://.** Öppnas `index.html` direkt från disk blockerar webbläsaren `fetch()`,
  och sidan visar då "Could not load the library".
- **HTTPS rekommenderas starkt.** Funktionen *Tilt to tumble* använder rörelsesensorn
  (`devicemotion`), som bara fungerar i säker kontext. På iPhone/iPad ber sidan om lov via
  `DeviceMotionEvent.requestPermission()` när funktionen slås på.
- **MIME-typer:** `.svg` ska skickas som `image/svg+xml`, `.json` som `application/json` och
  `.html` som `text/html; charset=utf-8`. Standard i nginx och Apache.
- **Cache:** `index.html` och `props/index.json` bör inte cachas hårt (t.ex. `Cache-Control: no-cache`),
  så att uppdateringar syns direkt. SVG-filerna kan cachas längre.
- Komprimering (gzip/brotli) av `.html`, `.json` och `.svg` är bra men inte nödvändig.
  Totalt rör det sig om under 2 MB.

Exempel för nginx (undermapp `/kalejdo/`):

```nginx
location /kalejdo/ {
    alias /var/www/kalejdo/;
    index index.html;
    location ~* \.(html|json)$ { add_header Cache-Control "no-cache"; }
    location ~* \.svg$        { add_header Cache-Control "public, max-age=604800"; }
}
```

För Apache räcker det att lägga filerna i en mapp under DocumentRoot.

## Uppladdning/uppdatering

- Kopiera `index.html` och hela `props/` till serverns mapp och behåll mappstrukturen.
  Använd t.ex. `rsync -av --delete index.html props user@vps:/var/www/kalejdo/` (utan snedstreck efter `props`, så att mappen följer med), eller scp/sftp.
- Används `--delete` försvinner prylar som tagits bort i källan även på servern.
  Det är bra, eftersom `index.json` då inte pekar på saknade filer.
- Kontrollera efteråt att `https://<domän>/<mapp>/props/index.json` går att öppna och att sidan
  visar biblioteket.

## Lägga till prylar

1. Lägg en `.svg` i rätt kategorimapp (eller i en ny mapp, så blir det en ny kategori).
   Filnamnet blir namnet i biblioteket: `taco_truck.svg` blir *Taco truck*.
2. Kör `python3 tools/build_index.py` från mappen där `index.html` ligger. Skriptet skriver om `props/index.json`.
3. Ladda upp både den nya SVG-filen och `props/index.json`.

SVG-filerna ska vara fristående, utan externa bilder eller typsnitt, och helst ha en kvadratisk `viewBox`.
Kategorin `evaq8` (utrymnings- och brandsäkerhetssymboler) ritas alltid med originalfärgerna,
även när *Mix colours* är påslaget (`KEEP_COLOURS` i `index.html`).

## Bra att veta om koden (index.html)

- Behållaren har fyra lager med lägena *Tumble*, *Float* och *Fixed*. Varje lager har en egen vinkel
  (`L.th`), vrids med huvudhastigheten × lagrets faktor (`L.speed`, 0,1–1,9) och kan gå åt motsatt
  håll (`L.rev`) eller vara låst (`L.locked`).
- Huvudreglaget (`S.spin`, 0–100) styr bara farten via `spinSpeed()`. Riktningen ligger i `S.dir` (1/-1).
  *Spin inertia* (`S.inertia`, 1–10) dämpar hur fort prylarna snurrar runt sin egen axel, och *Gravity*
  (`S.grav`, procent) skalar tyngdkraften i Tumble-lager.
- Fysiken körs i fast takt (120 Hz) i `physics()`. Bilden ritas i `frame()`: först behållaren på en
  dold canvas (`cham`), sedan speglas den i tårtbitar på `#view`, och dessutom ritas den lilla
  behållarbilden `#cell`.
- Helskärm (dubbeltryck) lägger mönstret sida vid sida: sexhörningar i bikakemönster vid 6 tårtbitar,
  och åttahörningar med snedställda kvadrater vid 8.
- `window.KalejdoApp` finns bara i Android-appen och används för att spara bilder i telefonens
  galleri. På webben laddas bilden i stället ner som PNG.
- Gränssnittet är på engelska. Kommentarerna i koden är på svenska.
