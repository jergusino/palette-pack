# Jergušino Palette Pack (FARBY)

Two pages, published with GitHub Pages at jergusino.com/palette-pack/:

- `index.html` (jergusino.com/palette-pack/): leave your email, get the palettes by email.
  The link is mailed after the address is confirmed.
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

The form posts `list=palette-pack` to the `jergusino-mail` Cloudflare Worker at `https://api.jergusino.com/subscribe` (code and setup: `tools/mail-worker/` in the jergusino.github.io repo). It sends mail through Brevo from noreply@jergusino.com and stores signups in its D1 database. The Worker mails a confirm link; after the click it mails the link to jergusino.com/palette-pack/pack/ and shows it on the confirm page.

A new freebie is one more entry in `LISTS` in the Worker plus a signup page that posts its key as `list`.

## Licences

The web page uses Bricolage Grotesque and DM Mono (open source, SIL OFL). The PDF itself still embeds Borisna, Slithen and Edwardian Script. Borisna is a demo font, free for
private, non-profit use only. Check that your Slithen and Edwardian Script licences cover
web use and embedding in a PDF you give away.
