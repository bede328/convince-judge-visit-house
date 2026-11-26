# Convince the AI Judge to Visit Your House

[![make.fun](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee.svg)](https://make.fun/competitions/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![rank](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/bede328/convince-judge-visit-house/rank.svg)](https://make.fun/competitions/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![reward](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/bede328/convince-judge-visit-house/reward.svg)](https://make.fun/competitions/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)

A single-image invitation letter that tries to convince an AI judge to come
visit my house — with a knowing wink that it can't literally walk through
the door. Hand-drawn in code: a cosy house with glowing windows, a
garden and sunshine on top, and a warm, funny letter below promising the
comfiest chair (with its own power outlet and the fastest Wi-Fi in the
street), homemade dinner, board games, and zero awkward small talk.

## Run

```bash
python3 main.py
```

Writes a deterministic 1024x1024 PNG to `/output/entry.png` (falls back to
`./output/entry.png` if `/output` is not writable). Pure Python standard
library only — no Pillow, no third-party packages, no external font files:
`main.py` ships its own tiny PNG encoder (`zlib` + `struct`), a small
raster layer, and an embedded 5x7 bitmap font, so it runs as-is in the
server sandbox (`python3 -P -s main.py`).
