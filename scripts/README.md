# Prostavěnost RD Kunín — jak aktualizovat dashboard

Dashboard: https://prostavenost-kunin.vercel.app
Repo: github.com/jakfej001/prostavenost-Kunin (branch `main`, auto-deploy na Vercel)

## Co je co

| Soubor | Role |
|--------|------|
| `data/prostavenost.json` | **Jediný zdroj pravdy** — období, fakturované součty (`auth`), položky (`items_active`, `items_zero`). |
| `scripts/gen_dashboard.py` | Generátor: z JSON přepíše konstanty `AUTH/D_A/D_Z` v `public/index.html`. UI/React kód nechá beze změny. |
| `scripts/inspect_xlsx.py` | Pomocník: z PAS11 xlsx vypíše položky po obdobích a **označí součtové `=SUM()` řádky** (ty se do položek NEpřidávají). |
| `public/index.html` | Nasazený dashboard. Vercel servíruje **jen `public/`** — `data/` a `scripts/` se nasazením ignorují, jsou v repu kvůli reprodukovatelnosti. |

## Dvě úrovně čísel (důležité — odsud plynul původní bug)

- **Dashboard (hlavní KPI) = FAKTUROVANÉ hodnoty.** P1–P3 z listu „Rekapitulace stavby", poslední období z **faktury Wobau** (bez DPH). To je `auth` v JSON.
- **Detail (položky) = položkový rozpad.** U posledního období může obsahovat i **dosud nefakturované vícepráce** → detail bývá o něco vyšší než fakturováno. Tento rozdíl je legitimní a dashboard ho v poznámce sám dopočítá.
- **NIKDY nezahrnuj do položek součtový `=SUM()` řádek** z xlsx (v O3 to byl „Řádek 1207" = `=SUM(AN79:AN1206)`, v O4 „Řádek 672"). Sečíst sloupec a pak ten součet přidat jako další položku = dvojí započtení (přesně to dělalo z P4 v Detailu 640 969 místo 347 919).

## Přidání nového období (např. „k 30.9.")

1. Ulož nový PAS11 xlsx do Drive: `…/Bydleni/Dum Kunin/Rekonstrukce/Wobau/Rekonstrukce/Fakturace/<období>/`.
2. Z **faktury Wobau** za období zjisti fakturovanou částku **bez DPH** (to je autoritativní total pro Dashboard).
3. (volitelně) `python3 scripts/inspect_xlsx.py <xlsx>` — vypíše položky a označí `=SUM()` řádky k vynechání.
4. Uprav `data/prostavenost.json`:
   - `auth.periods` → přidej label (např. `"k 30.9."`).
   - `auth.totP` a `auth.byObj[*].p` → doplň fakturované hodnoty období (z faktury / Rekapitulace).
   - `auth.cum` → součet `totP`.
   - `items_active` → ke každé dotčené položce přidej hodnotu na konec pole `p`. Nové vícepráce přidej jako nové položky (s rozumným popisem, ne „Řádek N").
5. Vygeneruj a zkontroluj:
   ```bash
   python3 scripts/gen_dashboard.py --data data/prostavenost.json --html public/index.html
   ```
   Report ukáže `Detail vs fakturováno` po obdobích. P1–P3 musí sedět na 0; u posledního období je kladný rozdíl = nefakturované vícepráce (OK).
6. Nasaď:
   ```bash
   git add -A && git commit -m "feat: prostavěnost k 30.9." && git push origin main
   ```
   Vercel se přenasadí sám (~1 min). Pak hard refresh `Cmd+Option+R` na dashboardu.

## Pozn.

- Drag-drop upload xlsx přímo v dashboardu funguje, ale je **jen lokální** (localStorage v prohlížeči) — nenasazuje se a nesdílí. Zdroj pravdy je `data/prostavenost.json` + git. Tlačítko „↺ Reset" vrátí na nasazený baseline.
- V kořeni repa leží starší `index.html` (mimo `public/`) — nasazení ho neřeší, je to legacy.
