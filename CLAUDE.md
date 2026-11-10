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
store/catalog.json    butikens katalog: paket, pris, beskrivning, förhandsbilder
store/packs/<id>.json butikspaketen (gratis = vanlig JSON med SVG-kod, betalda = krypterade)
store-src/<id>/       källfiler (SVG + pack.json) för GRATISpaket
tools/build_index.py  bygger om props/index.json från mapparna i props/
tools/build_pack.py   bygger ett butikspaket från en källmapp och för in det i store/catalog.json
CLAUDE.md             den här filen
butik-kalla/          (bara på Dicks dator) källfiler och koder för BETALDA paket – PRIVAT
```

Kategorimapparna är: `glass`, `gems`, `shapes`, `nature`, `food`, `critters`, `things`, `electro`, `christmas`
och `evaq8`. Visningsnamn och ordning finns i `tools/build_index.py`, och en mapp kan också ha en
`_category.txt` med sitt namn.

Endast `index.html`, `props/` och `store/` behövs på webbservern. `tools/`, `store-src/` och
`CLAUDE.md` ska inte publiceras. De gör ingen skada, men behövs inte.

**`butik-kalla/` får ALDRIG laddas upp till webbservern eller läggas i GitHub-repot** (repot är publikt).
Den innehåller de okrypterade betalpaketen och upplåsningskoderna.

## Hur sidan startar

1. `index.html` hämtar `props/index.json` med `fetch()` (relativ sökväg).
2. Prylarna hämtas också med `fetch()` (relativt, `props/...svg`), görs om till bilder och ritas på `<canvas>`.
3. Installerade butikspaket läses från `localStorage` (`kalejdo.packs.v1`) och läggs in som kategorier.
4. Användarens kalejdoskop (lager, prylar, inställningar) sparas i `localStorage` under nyckeln
   `kalejdo.v1`. Sparade kalejdoskop ("My kaleidoscopes") ligger i `kalejdo.saves.v1`, och koder till
   upplåsta betalpaket i `kalejdo.codes.v1`. Det finns ingen inloggning, och inget skickas till någon server.

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

- Kopiera `index.html`, hela `props/` och hela `store/` till serverns mapp och behåll mappstrukturen.
  Använd t.ex. `rsync -av --delete index.html props store user@vps:/var/www/kalejdo/` (utan snedstreck efter mappnamnen, så att mapparna följer med), eller scp/sftp.
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

## Butiken

- Butiken öppnas med chipet **Shop** först i biblioteket, eller via ⋯. Den läser `store/catalog.json`
  och visar paketen med förhandsbilder och pris (Free eller t.ex. 19 kr).
- **Gratispaket:** knappen *Get* hämtar `store/packs/<id>.json` och installerar paketet. Det sparas i
  webbläsaren/appen och fungerar sedan utan nät.
- **Betalda paket:** filen är krypterad (AES-256-GCM, nyckel från upplåsningskoden via PBKDF2-SHA256,
  200 000 varv). Användaren trycker *Buy*, som öppnar paketets `buyUrl` (t.ex. en Stripe Payment Link
  eller en Swish-sida), och skriver sedan in koden under *I have a code*. Koden normaliseras
  (versaler, bara A–Z/0–9). Upplåsningen kräver https, eller localhost, eftersom WebCrypto kräver säker kontext.
- Det finns ingen server som kontrollerar köp. Alla köpare av ett paket får samma kod.
  Riktig köpkontroll per kund kräver en backend eller Google Play Billing.

### Lägga till eller uppdatera ett paket

1. Skapa en källmapp med SVG-filerna och en `pack.json` (se dokumentationen överst i `tools/build_pack.py`).
   Gratispaket läggs i `store-src/<id>/`. Betalda paket läggs i `butik-kalla/<id>/`, aldrig i repot.
2. Bygg:
   - gratis: `python3 tools/build_pack.py store-src/<id>`
   - betalt: `python3 tools/build_pack.py butik-kalla/<id> --code <KOD>` (kräver `pip install cryptography`)
3. Höj `version` i `pack.json` när innehållet ändras. Användare som har paketet får då knappen *Update*.
   Betalda paket uppdateras automatiskt med den sparade koden. Byt därför inte kod för ett befintligt paket.
4. Ladda upp `store/catalog.json` och `store/packs/<id>.json`, och committa samma filer till GitHub
   så att nästa app-bygge får med dem.

### Butiken i Android-appen

- Appen har en kopia av `store/` inbyggd, så butiken fungerar utan nät men visar bara de paket
  som fanns när appen byggdes.
- För att appen ska hämta nya paket från webbservern: sätt `STORE_REMOTE` i `index.html` till t.ex.
  `"https://<domän>/kalejdo/store/"` och bygg om appen. Servern måste då tillåta CORS för `store/`,
  eftersom appens sidor har ursprunget `https://appassets.androidplatform.net`:

```nginx
location /kalejdo/store/ {
    alias /var/www/kalejdo/store/;
    add_header Access-Control-Allow-Origin "*";
    add_header Cache-Control "no-cache";
}
```

- Köpknappen öppnar `buyUrl` i telefonens webbläsare via `KalejdoApp.openUrl()`.

## Bra att veta om koden (index.html)

- Behållaren har fyra lager med lägena *Tumble*, *Float* och *Fixed*. Varje lager har en egen vinkel
  (`L.th`), vrids med huvudhastigheten × lagrets faktor (`L.speed`, 0,1–1,9) och kan gå åt motsatt
  håll (`L.rev`) eller vara låst (`L.locked`).
- Huvudreglaget (`S.spin`, 0–100) styr bara farten via `spinSpeed()`. Riktning finns bara per lager (`L.rev`).
  *Spin inertia* (`S.inertia`, 1–10) dämpar hur fort prylarna snurrar runt sin egen axel, och *Gravity*
  (`S.grav`, procent) skalar tyngdkraften i Tumble-lager.
- Fysiken körs i fast takt (120 Hz) i `physics()`. Bilden ritas i `frame()`: först behållaren på en
  dold canvas (`cham`), sedan speglas den i tårtbitar på `#view`, och dessutom ritas den lilla
  behållarbilden `#cell`.
- Helskärm (dubbeltryck) lägger mönstret sida vid sida: sexhörningar i bikakemönster vid 6 tårtbitar,
  och åttahörningar med snedställda kvadrater vid 8.
- `window.KalejdoApp` finns bara i Android-appen. Den används för att spara bilder i telefonens galleri
  (`saveImage`) och för att öppna köplänkar (`openUrl`). På webben laddas bilden i stället ner som PNG,
  och länkar öppnas i en ny flik.
- Butikspaketens prylar får kategori-id `pack-<id>` och pryl-id `pack-<id>/<namn>`. Prylarnas SVG-kod
  ligger i minnet (`PROPS[id].svg`) i stället för som fil.
- Gränssnittet är på engelska. Kommentarerna i koden är på svenska.
