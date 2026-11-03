# Jergušino Palette Pack (FARBY)

Two pages, published with GitHub Pages at jergusino.com/palette-pack/:

- `index.html` (jergusino.com/palette-pack/): leave your email, get the palettes by email.
  Every signup gets the link, whether or not the address is already in the sheet.
- `pack/` (jergusino.com/palette-pack/pack/): the download page. A button downloads
  `pack/palette-pack.pdf` (15 pages, 1080 × 1350), and all 12 palettes are
  shown on the page; clicking a colour copies its HEX code.

Same setup as jergusino.com/font-tool/, only the freebie is different.

## Changing the palettes

The PDF is built by `tools/build_pdf.py` (needs `pip install reportlab fonttools`):

```
python3 tools/build_pdf.py
```

It uses the site's own fonts from `assets/fonts/` and the card lockup in `tools/lockup.png`,
and overwrites `pack/palette-pack.pdf`. The colours on `pack/index.html` are
written into the page, so if you change `PALETTES`, change the page too (or ask Claude to
regenerate it).

## The email

The form posts to the same Google Apps Script as the newsletter and the Font Tool
(`apps-script/Code.gs`), with `list=palette-pack`. The script:

- writes the signup into the **Subscribers** tab of the "Newsletter signups" sheet, with
  **List** = `palette-pack` (once per address),
- emails the link to jergusino.com/palette-pack/pack/ straight away, every time it is asked for.

Freebies live in the `FREEBIES` table at the top of `Code.gs` (`font-tool`, `palette-pack`).
A new freebie is one more entry there plus a signup page that posts its key as `list`.

After changing `Code.gs`, paste it into Apps Script and deploy a **New version**
(Deploy → Manage deployments → pencil → Version: New version). The /exec link stays the same.
The newsletter and font-tool repos have older copies of this file; this one replaces them.

## Licences

The PDF embeds Borisna, Slithen and Edwardian Script. Borisna is a demo font, free for
private, non-profit use only. Check that your Slithen and Edwardian Script licences cover
web use and embedding in a PDF you give away.
