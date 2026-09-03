# Client deck — source

Both language versions are generated from `build_deck.py`. Edit the script, never the HTML:
the two decks share their structure, motion and SVG assets, so editing one HTML by hand is how
the Arabic and English versions drift apart.

```bash
cd runbooks/ai-features/deck && python3 build_deck.py
# writes ../08-boardhub-deck-en.html and ../09-boardhub-deck-ar.html
```

No dependencies — standard library only.

## What lives where

| In the script | What it controls |
|---|---|
| `MODULES` | the platform's 16 modules and which business function each belongs to. Taken from the running BoardHub sidebar; update it when the product's navigation changes. |
| `CLUSTERS` | the four business functions the modules group into. |
| `EN` / `AR` | all copy. Same keys in both, so a missing translation shows up as a `KeyError` rather than silently shipping English into the Arabic deck. |
| `svg_overwhelmed` / `svg_system_map` / `svg_octopus` | the three illustrations, drawn inline. |
| `ui_mock` | the stylised product screens, built from the real navigation labels. |
| `CSS` / `JS` | shared styling and slide navigation. |

## Re-targeting to another client

Change `client` and `client_sub` in both `EN` and `AR`. Nothing else is client-specific.

## Notes

- The logo is `logo-light.b64` — a reversed version of `masarcorp/masarcorp-brand-assets/logo.png`,
  with the dark navy ink recoloured near-white and the green mark preserved, because the original
  artwork disappears on the dark slides.
- Illustrations are inline SVG rather than unDraw/Storyset assets: the published artifact sandbox
  blocks external images, and stock figures read as clip-art in a government room.
- The corner timestamps pace a 15-minute session ending in a live demo. They are a guide for the
  presenter, not a script.
