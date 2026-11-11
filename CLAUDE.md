# Kalejdo – webbsida och Android-app

Kalejdo är ett kalejdoskop. Speglarna visar en tårtbit av en rund behållare med små SVG-prylar,
och bilden byggs upp av 6 eller 8 speglade tårtbitar. Exakt samma kod (`index.html` + `props/` + `store/`)
körs som **webbsida** och, inuti ett tunt WebView-skal, som **Android-app**.

- Ägare: Dick (GitHub `skitknas-ctrl`)
- Källa: https://github.com/skitknas-ctrl/Kalejdo, gren `main`. Repot är **publikt**.
- Den här mappen (`P:\Appar\Kalejdo\`) är Dicks arbetskopia. Därifrån utvecklas både webbsidan och appen,
  därifrån pushas ändringar till GitHub och därifrån laddas webbsidan upp till VPS:en.
  Redigera inte filerna direkt på servern.
- Webbsidan är helt statisk. Den har ingen backend, ingen databas, inget PHP, inga cookies, inga externa
  beroenden, inget CDN och inga typsnitt utifrån.

## Arbetssätt med Dick

- Svara på svenska. Börja varje svar med dagens datum i formatet ÅÅMMDD (t.ex. 261110).
- Skriv i punktform med bokstäver (A, B, C …). Bokstäverna löper vidare genom hela konversationen:
  slutade förra svaret på D börjar nästa på E, och efter Z kommer AA, AB osv. Underpunkter skrivs B1, B2.
  Dick hänvisar till punkter, t.ex. "Angående R".
- Numrerade listor ska skrivas så att numren följer med vid kopiering.
- I Android-appar får innehåll aldrig ligga så högt upp att det krockar med statusfältet (klocka, batteri osv.).
- Gränssnittet i appen är på engelska. Kommentarerna i koden är på svenska.
- Testa ändringar i en webbläsare i mobilformat (t.ex. 412×892) innan de pushas.
  Kör sidan via en lokal webbserver: `python -m http.server 8765` i den här mappen, och öppna sedan `http://localhost:8765/`.
- Efter varje push till `main` bygger GitHub Actions en ny test-APK. Kontrollera att bygget går igenom
  (`gh run list -R skitknas-ctrl/Kalejdo -L 1`) och ge Dick länken:
  https://github.com/skitknas-ctrl/Kalejdo/releases/latest/download/kalejdo-debug.apk

## Filer

```
index.html              hela appen: HTML + CSS + JavaScript i en fil
props/index.json        listan över alla inbyggda prylar (kategorier -> filer); läses av index.html vid start
props/<kategori>/*.svg  de inbyggda prylarna, en SVG per pryl (viewBox 0 0 100 100)
store/catalog.json      butikens katalog: paket, pris, beskrivning, förhandsbilder
store/packs/<id>.json   butikspaketen (gratis = vanlig JSON med SVG-kod, betalda = krypterade)
store-src/<id>/         källfiler (SVG + pack.json) för GRATISpaket
tools/build_index.py    bygger om props/index.json från mapparna i props/
tools/build_pack.py     bygger ett butikspaket från en källmapp och för in det i store/catalog.json
tools/generators/       Python-skripten som ritade de inbyggda prylarna (hjälp om man vill rita om/fler)
app/                    Android-skalet (Kotlin), se "Android-appen" nedan
build.gradle.kts, settings.gradle.kts, gradle.properties, gradlew, gradlew.bat, gradle/wrapper/
                        Gradle-bygget för appen
.github/workflows/build.yml  GitHub Actions: bygger test-APK vid varje push och release-APK vid taggar
design/skarmbild.png    skärmbild till README
README.md               beskrivning för användare (svenska)
CLAUDE.md               den här filen
butik-kalla/            PRIVAT, bara på Dicks dator: källfiler och koder för BETALDA paket (står i .gitignore)
```

Kategorimapparna i `props/` är: `glass`, `gems`, `shapes`, `nature`, `food`, `critters`, `things`, `electro`,
`christmas` och `evaq8`. Visningsnamn och ordning finns i `tools/build_index.py`, och en mapp kan också ha en
`_category.txt` med sitt namn.

**`butik-kalla/` får ALDRIG laddas upp till webbservern eller läggas i GitHub-repot.** Repot är publikt,
och mappen innehåller de okrypterade betalpaketen och upplåsningskoderna. Den står i `.gitignore`.
Kontrollera med `git status` före varje commit att inget därifrån följer med.

## GitHub

### Första gången: gör mappen till en git-arbetskopia

Filerna i den här mappen kopierades hit utan git-historik. Vissa kopior (SVG-filer och PNG) fick dessutom
automatiskt ett metadata-block (C2PA) under kopieringen och skiljer sig därför från GitHub. Mappen `.github/`
(byggflödet) gick inte att kopiera hit alls. Allt som finns
här finns också på GitHub, utom `butik-kalla/`. Koppla därför mappen till repot och ta GitHubs versioner:

```
cd P:\Appar\Kalejdo
git init -b main
git remote add origin https://github.com/skitknas-ctrl/Kalejdo.git
git fetch origin
git reset --hard origin/main
git branch --set-upstream-to=origin/main main
git status
```

`git reset --hard` skriver över alla filer som finns i repot med GitHubs versioner. Ospårade och ignorerade
filer, som `butik-kalla/`, lämnas orörda. Efteråt ska `git status` visa en ren arbetskopia.

### Inloggning

- Pushning kräver att Dick är inloggad på GitHub på datorn. Enklast är GitHub CLI: `gh auth login`
  (välj GitHub.com, HTTPS och logga in i webbläsaren). Därefter fungerar `git push`, och `gh` kan läsa
  Actions-status och releaser.
- Alternativt sköter Git Credential Manager (följer med Git för Windows) inloggningen första gången man pushar.
- Lägg aldrig in token eller lösenord i filer i den här mappen.
- Commit-författare: `git config user.name "Dick"` och `git config user.email <Dicks GitHub-mejl>`.
  Fråga Dick om adressen om den saknas. Han kan också använda GitHubs noreply-adress.

### Vardagsflöde

```
git pull
# ... ändra, testa lokalt ...
git status                      # kontrollera att butik-kalla/ inte är med
git add -A
git commit -m "Kort beskrivning på svenska"
git push
gh run list -R skitknas-ctrl/Kalejdo -L 1    # vänta tills bygget är "completed success"
```

- Skriv commit-meddelanden på svenska och beskriv vad som ändrats och varför.
- Commita direkt på `main`. Det är Dicks eget projekt och det finns inga pull request-rutiner.

### Byggen och releaser (GitHub Actions, `.github/workflows/build.yml`)

- **Varje push till `main`:** kör `tools/build_index.py` och `./gradlew test assembleDebug` med
  `-PbuildNumber=<körningsnummer>`. Testbygget publiceras som release `0.1.0-test.<n>` och är markerat som senaste.
  De tre senaste testreleaserna sparas och äldre tas bort. Stabil nedladdningslänk:
  https://github.com/skitknas-ctrl/Kalejdo/releases/latest/download/kalejdo-debug.apk
- Testbyggena signeras med testnyckeln `app/debug.keystore` (lösenord `android`, publik med flit), så att
  varje nytt testbygge kan installeras ovanpå det förra. Appen har id `io.github.skitknasctrl.kalejdo.debug`.
- **Tagg `v*`** (t.ex. `git tag v1.0.0 && git push origin v1.0.0`): bygger en release-APK
  (`io.github.skitknasctrl.kalejdo`) och skapar en GitHub-release. Den signeras om repot har secrets
  `RELEASE_KEYSTORE_BASE64`, `RELEASE_KEYSTORE_PASSWORD`, `RELEASE_KEY_ALIAS` och `RELEASE_KEY_PASSWORD`.
  Annars blir den osignerad. Den riktiga release-nyckeln finns inte än, och den får aldrig committas.
- Versionen sätts i `app/build.gradle.kts` (`baseVersion`, nu `0.1.0`).

## Android-appen

- Ett WebView-skal i `app/src/main/kotlin/io/github/skitknasctrl/kalejdo/MainActivity.kt`.
  Gradle-uppgiften `copyWeb` i `app/build.gradle.kts` kopierar `index.html`, `props/` och `store/` från repots
  rot till appens assets vid varje bygge. Ändringar i webbsidan följer alltså automatiskt med i appen.
  Det finns ingen separat kopia att hålla i synk.
- Sidan laddas via `WebViewAssetLoader` från `https://appassets.androidplatform.net/assets/index.html`.
  Därför fungerar `fetch()`, `localStorage` och WebCrypto som på en vanlig https-sida.
- Stående läge, skärmen hålls tänd, och system-insets (statusfält, utskärning, navigeringsfält) läggs som
  padding så att innehållet aldrig hamnar under statusfältet.
- `minSdk 29` (Android 10), `targetSdk`/`compileSdk 35`, Kotlin 2.0.21, AGP 8.7.3, Gradle 8.9, Java 17.
  Beroenden: appcompat, core-ktx, webkit. Inga Google Play-tjänster (appen ska kunna gå till F-Droid).
- Behörigheter: `VIBRATE` (skaka) och `INTERNET` (butiken när `STORE_REMOTE` pekar på en server).
- JavaScript-bryggan `window.KalejdoApp`:
  - `saveImage(base64Png, fileName)` sparar en bild i Bilder/Kalejdo via MediaStore, utan behörighetsfråga.
  - `openUrl(url)` öppnar en http(s)-länk i telefonens webbläsare (köpknappen i butiken).
  - Allt annat navigerande i WebView blockeras.
- Ikonen är en vektor (`res/drawable/ic_launcher_foreground.xml`): sex färgade tårtbitar i en mässingsring.
- Det finns ingen Android Studio-installation i flödet. Allt byggs i GitHub Actions. Lokalt bygge går också om
  JDK 17 och Android SDK finns: `gradlew.bat assembleDebug`.

## Webbsidan

### Hur sidan startar

1. `index.html` hämtar `props/index.json` med `fetch()` (relativ sökväg).
2. Prylarna hämtas också med `fetch()` (relativt, `props/...svg`), görs om till bilder och ritas på `<canvas>`.
3. Installerade butikspaket läses från `localStorage` (`kalejdo.packs.v1`) och läggs in som kategorier.
4. Användarens kalejdoskop (lager, prylar, inställningar) sparas i `localStorage` under nyckeln
   `kalejdo.v1`. Sparade kalejdoskop ("My kaleidoscopes") ligger i `kalejdo.saves.v1`, och koder till
   upplåsta betalpaket i `kalejdo.codes.v1`. Det finns ingen inloggning, och inget skickas till någon server.

Alla sökvägar är relativa. Därför fungerar sidan både i roten (`https://exempel.se/`) och i en
undermapp (`https://exempel.se/kalejdo/`) utan ändringar.

### Krav på webbservern

- **http(s), inte file://.** Öppnas `index.html` direkt från disk blockerar webbläsaren `fetch()`,
  och sidan visar då "Could not load the library".
- **HTTPS rekommenderas starkt.** Funktionen *Tilt to tumble* använder rörelsesensorn
  (`devicemotion`), som bara fungerar i säker kontext. På iPhone/iPad ber sidan om lov via
  `DeviceMotionEvent.requestPermission()` när funktionen slås på. Upplåsning av betalpaket (WebCrypto)
  kräver också https.
- **MIME-typer:** `.svg` ska skickas som `image/svg+xml`, `.json` som `application/json` och
  `.html` som `text/html; charset=utf-8`. Standard i nginx och Apache.
- **Cache:** `index.html`, `props/index.json` och `store/` bör inte cachas hårt (t.ex. `Cache-Control: no-cache`),
  så att uppdateringar syns direkt. SVG-filerna kan cachas längre.
- Komprimering (gzip/brotli) av `.html`, `.json` och `.svg` är bra men inte nödvändig.

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

### Uppladdning/uppdatering

- Endast `index.html`, `props/` och `store/` behövs på webbservern. `app/`, `tools/`, `store-src/`, Gradle-filerna,
  `.github/` och `CLAUDE.md` ska inte publiceras, och `butik-kalla/` aldrig.
- Ladda upp de tre med t.ex. `rsync -av --delete index.html props store user@vps:/var/www/kalejdo/`
  (utan snedstreck efter mappnamnen, så att mapparna följer med), eller med scp/sftp.
- Används `--delete` försvinner prylar som tagits bort i källan även på servern.
  Det är bra, eftersom `index.json` då inte pekar på saknade filer.
- Kontrollera efteråt att `https://<domän>/<mapp>/props/index.json` går att öppna och att sidan visar biblioteket.
- Publicera webbsidan från samma commit som finns på GitHub, så att webb och app är i takt.

### Lägga till prylar

1. Lägg en `.svg` i rätt kategorimapp (eller i en ny mapp, så blir det en ny kategori).
   Filnamnet blir namnet i biblioteket: `taco_truck.svg` blir *Taco truck*.
2. Kör `python tools/build_index.py`. Skriptet skriver om `props/index.json`.
   Actions kör det också före varje app-bygge.
3. Committa och pusha. Ladda upp både den nya SVG-filen och `props/index.json` till webbservern.

SVG-filerna ska vara fristående, utan externa bilder eller typsnitt, och helst ha en kvadratisk `viewBox`.
Kategorin `evaq8` (utrymnings- och brandsäkerhetssymboler) ritas alltid med originalfärgerna,
även när *Mix colours* är påslaget (`KEEP_COLOURS` i `index.html`). Storleken som nya prylar får per kategori
står i `CAT_SIZE` i `index.html`.

SVG-filerna i `props/` är källan. Skripten i `tools/generators/` ritade dem från början och kan användas som
utgångspunkt för nya prylar i samma stil. Kör dem inte rakt av, eftersom de skriver över befintliga filer.

## Butiken

- Butiken öppnas med chipet **Shop** först i biblioteket, eller via ⋯. Den läser `store/catalog.json`
  och visar paketen med förhandsbilder och pris (Free eller t.ex. 19 kr).
- **Gratispaket:** knappen *Get* hämtar `store/packs/<id>.json` och installerar paketet. Det sparas i
  webbläsaren/appen och fungerar sedan utan nät.
- **Betalda paket:** filen är krypterad (AES-256-GCM, nyckel från upplåsningskoden via PBKDF2-SHA256,
  200 000 varv). Användaren trycker *Buy*, som öppnar paketets `buyUrl` (t.ex. en Stripe Payment Link
  eller en Swish-sida), och skriver sedan in koden under *I have a code*. Koden normaliseras
  (versaler, bara A–Z/0–9).
- Det finns ingen server som kontrollerar köp. Alla köpare av ett paket får samma kod.
  Riktig köpkontroll per kund kräver en backend (Dick har diskuterat ett PHP + databas-API på VPS:en
  där servern kontrollerar koden och bara då lämnar ut SVG-filerna) eller Google Play Billing.
- Paket just nu: **Ocean** (gratis, 27 prylar sedan version 2 2026-11-11, ritade av `tools/generators/make_ocean.py`, källa i `store-src/ocean/`) och **Space** (19 kr, 14 prylar,
  källa och kod i `butik-kalla/`).

### Lägga till eller uppdatera ett paket

1. Skapa en källmapp med SVG-filerna och en `pack.json` (se dokumentationen överst i `tools/build_pack.py`).
   Gratispaket läggs i `store-src/<id>/`. Betalda paket läggs i `butik-kalla/<id>/`, aldrig i repot.
2. Bygg:
   - gratis: `python tools/build_pack.py store-src/<id>`
   - betalt: `python tools/build_pack.py butik-kalla/<id> --code <KOD>` (kräver `pip install cryptography`)
3. Höj `version` i `pack.json` när innehållet ändras. Användare som har paketet får då knappen *Update*.
   Betalda paket uppdateras automatiskt med den sparade koden. Byt därför inte kod för ett befintligt paket.
4. Committa `store/catalog.json` och `store/packs/<id>.json` (så att nästa app-bygge får med dem) och
   ladda upp samma filer till webbservern.

### Butiken i Android-appen

- Appen har en kopia av `store/` inbyggd, så butiken fungerar utan nät men visar bara de paket
  som fanns när appen byggdes.
- Sedan 2026-11-11 pekar `STORE_REMOTE` på `https://gr8eam.com/Kalejdo/api/store.php?f=` (katalog och paket byggs ur
  gr8eam_db för kategorier som admin bockat "Erbjud i Android-appens butik"). `loadCatalog()` slår ihop den inbyggda
  butiken med serverns; varje paket minns sin `base`. Serverns paket är gratis; versionen är en tidsstämpel som växer
  vid ändringar, så appen visar Update. Hela paketet sparas i localStorage, så håll paketen under ett par MB.
- Mix colours togs bort 2026-11-11 (Dick): prylar visas alltid i sina egna färger (`raster()` ignorerar hue, `keepColours` är utan verkan).
- Så här var det tänkt före 2026-11-11: sätt `STORE_REMOTE` i `index.html` till t.ex.
  `"https://<domän>/kalejdo/store/"`, committa och pusha. Servern måste då tillåta CORS för `store/`,
  eftersom appens sidor har ursprunget `https://appassets.androidplatform.net`:

```nginx
location /kalejdo/store/ {
    alias /var/www/kalejdo/store/;
    add_header Access-Control-Allow-Origin "*";
    add_header Cache-Control "no-cache";
}
```

## Bra att veta om koden (index.html)

- Behållaren har fyra lager med lägena *Tumble*, *Float* och *Fixed*. Varje lager har en egen vinkel
  (`L.th`), vrids med huvudhastigheten × lagrets faktor (`L.speed`, 0,1–1,9) och kan gå åt motsatt
  håll (`L.rev`) eller vara låst (`L.locked`, STOP-märket). Högst 40 prylar per lager.
- Huvudreglaget (`S.spin`, 0–100) styr bara farten via `spinSpeed()`. Riktning finns bara per lager (`L.rev`).
  *Spin inertia* (`S.inertia`, 1–10) dämpar hur fort prylarna snurrar runt sin egen axel, och *Gravity*
  (`S.grav`, procent) skalar tyngdkraften i Tumble-lager.
- Fysiken körs i fast takt (120 Hz) i `physics()`. Bilden ritas i `frame()`: först behållaren på en
  dold canvas (`cham`), sedan speglas den i tårtbitar på `#view`, och dessutom ritas den lilla
  behållarbilden `#cell`. I den kan man vrida och trycka bort prylar.
- Helskärm (dubbeltryck) lägger mönstret sida vid sida: sexhörningar i bikakemönster vid 6 tårtbitar,
  och åttahörningar med snedställda kvadrater vid 8. Ett enkeltryck på kalejdoskopet stoppar eller startar rotationen.
- Sparade lägen migreras i `start()`. Äldre fält (negativ `spin`, `S.dir`, `lockTheta`) görs om.
  Lägg till migrering där om datamodellen ändras, så att användarnas sparade kalejdoskop fortsätter att fungera.
- `window.KalejdoApp` finns bara i Android-appen (se ovan). På webben laddas bilder ner som PNG och
  länkar öppnas i en ny flik.
- Butikspaketens prylar får kategori-id `pack-<id>` och pryl-id `pack-<id>/<namn>`. Prylarnas SVG-kod
  ligger i minnet (`PROPS[id].svg`) i stället för som fil.
- iPhone: rörelsesensorns axlar har omvänt tecken mot Android (`IOS` i koden), och sensorn kräver
  `requestPermission()` efter ett tryck.
