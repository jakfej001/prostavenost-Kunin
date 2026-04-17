# Prostavěnost RD Kunín č.p. 393

Interaktivní dashboard prostavěnosti stavby s AI chatbotem.

## Funkce
- 📊 Dashboard — KPI, grafy, 3 období (P1/P2/P3)
- 📋 Detail — 149 položek, fulltext, filtry, řazení
- 💬 Dotazy — Claude AI chatbot nad rozpočtovými daty
- 🔄 Změny — automatický diff při uploadu nového xlsx
- 📦 Verze — localStorage historie

## Deploy na Vercel

### 1. Git repozitář
```bash
cd prostavěnost-kunin
git init && git add . && git commit -m "init"
git remote add origin git@github.com:USER/prostavěnost-kunin.git
git push -u origin main
```

### 2. Vercel
1. vercel.com → Add New → Project → Import repozitář
2. Settings → Environment Variables → přidej:
   - Name: `ANTHROPIC_API_KEY`
   - Value: `sk-ant-...` (tvůj klíč)
3. Deploy

### 3. Vlastní doména (volitelné)
Settings → Domains → `stavba.fejfar.cz`
DNS: CNAME `stavba` → `cname.vercel-dns.com`

## Architektura chatu
```
Prohlížeč → POST /api/chat → Vercel Function → Anthropic API
                                  ↑ API klíč z env
```
API klíč nikdy neopustí server.

## Aktualizace dat
Nahraj nový xlsx přes tlačítko 📂 v dashboardu.
Parser automaticky detekuje KROS formát.
