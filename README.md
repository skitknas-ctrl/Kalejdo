# Kalejdo

Ett kalejdoskop för mobilen. Speglarna visar en tårtbit av behållaren längst fram i tuben,
och bilden byggs upp av 6 eller 8 speglade tårtbitar. Behållaren fylls med små roliga prylar
ur ett bibliotek med SVG-filer, i fyra lager som fylls var för sig.

![Skärmbild](design/skarmbild.png)

## Så fungerar det

- **Kalejdoskopet** överst. Dra runt med fingret för att vrida behållaren. Dubbeltryck för helskärm
  (dubbeltryck igen för att få tillbaka kontrollerna).
- **6 / 8** väljer antal tårtbitar.
- **Snurr-reglaget** vrider behållaren av sig själv, åt vänster eller höger. Mitten är stilla.
- **Skaka** ger allt löst i behållaren en knuff.
- **Ljus** växlar bakgrundsljuset: Daylight, Warm lamp, Sky, Sunset, Night och Rainbow.
- **Kameran** sparar bilden i *Bilder/Kalejdo* (i webbläsaren laddas den ner).

## Behållaren och lagren

- Den lilla runda bilden till vänster är behållaren. Den streckade tårtbiten visar vilken del speglarna ser.
  Dra i den för att vrida, tryck på en pryl för att ta bort den (i valt lager, med Ångra).
- Det finns fyra lager, **1–4**. Siffran under visar hur många prylar lagret har (högst 40).
  Lager 1 ritas längst bak och lager 4 längst fram.
- Varje lager har ett eget beteende:
  - **Tumble:** prylarna faller, rullar och studsar när behållaren vrids.
  - **Float:** prylarna svävar tyngdlöst och följer långsamt med vätskan.
  - **Fixed:** prylarna sitter fast och vrids med behållaren.
- Ögat döljer eller visar lagret, reglaget ändrar genomskinligheten, tärningen fyller på med
  tio slumpvisa prylar (ur vald kategori) och papperskorgen tömmer lagret.
- Allt sparas i telefonen, så kalejdoskopet ser likadant ut nästa gång.

## Biblioteket

- Tryck på en pryl för att släppa ner den i valt lager.
- **Mix colours** ger varje ny pryl en slumpad färgton. Stäng av för originalfärgerna.
- Storleksreglaget gäller nya prylar.
- Under **⋯** finns *Tilt to tumble* (tyngdkraften följer hur man håller telefonen), *Field of view*
  (hur stor del av behållaren speglarna ser), helskärm, töm allt och startblandningen.

## Egna prylar

Prylarna är vanliga SVG-filer i `props/<kategori>/`. Det finns 122 stycken i sju kategorier:
glas och pärlor, ädelstenar, former, natur, mat, djur och saker.

- Lägg till en pryl genom att ladda upp en `.svg` i en kategorimapp, t.ex. `props/food/taco.svg`.
  Filnamnet blir namnet i biblioteket (`taco` → *Taco*).
- En ny mapp blir en ny kategori. Vill du ge den ett snyggare namn, lägg en fil `_category.txt`
  med namnet på första raden i mappen.
- Rita prylen så att den fyller en kvadratisk `viewBox` (t.ex. `0 0 100 100`) med lite marginal.
- GitHub Actions kör `tools/build_index.py` före varje bygge, så nya filer kommer med i appen automatiskt.
  För webbversionen kör man skriptet själv och checkar in `props/index.json`.

## Teknik

- Själva kalejdoskopet är `index.html` plus `props/`, utan beroenden. Det går att köra i en webbläsare
  (via en webbserver eller GitHub Pages, inte som lös fil).
- Android-appen är ett tunt WebView-skal i stående läge. Innehållet hålls innanför statusfältet och
  navigeringsfältet.
- GitHub Actions bygger en test-APK vid varje push till `main`. Den publiceras som
  senaste release: `releases/latest/download/kalejdo-debug.apk`.
- Appen kräver Android 10 eller senare. Den har inga annonser och ingen spårning, och den använder inget nätverk.
