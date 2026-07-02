# Hood Trade — landing page

A self-contained, single-file landing page (`index.html`) for the Hood Trade agent.
No build step, no dependencies — just static HTML/CSS/JS.

## Preview locally

Open the file directly in a browser:

```bash
open index.html          # macOS
```

Or serve it with Python's built-in server:

```bash
cd site
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Deploy to Vercel

Production site: **[hoodtrade.pro](https://hoodtrade.pro)**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/hoodtradeprofile/hoodtrade&root-directory=site&project-name=hoodtrade&repository-name=hoodtrade)

### Option A — Vercel dashboard (no CLI)

1. Push the repo to GitHub (`github.com/hoodtradeprofile/hoodtrade`).
2. Go to [vercel.com/new](https://vercel.com/new) and **Import** the repo.
3. Set **Root Directory** to `site`, and Framework Preset to **Other**.
4. Click **Deploy** → you get `hoodtrade.vercel.app`, then add the custom domain **hoodtrade.pro** in Vercel → Settings → Domains.

### Option B — Vercel CLI

```bash
npm i -g vercel
cd site
vercel --prod
```

The first run asks you to log in and links the project. `vercel.json` in this
folder handles clean URLs and security headers automatically.

## Deploy to GitHub Pages (alternative)

Move `index.html` to `/docs` (or the repo root), then enable Pages in
**Settings → Pages → Source: main / /docs**. The site publishes at
`hoodtradeprofile.github.io/hoodtrade` (or your custom domain `hoodtrade.pro`).
