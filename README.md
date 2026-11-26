# Convince the AI Judge to Visit Your House

[![make.fun](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee.svg)](https://make.fun/competitions/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![rank](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/bede328/convince-judge-visit-house/rank.svg)](https://make.fun/competitions/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![reward](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/bede328/convince-judge-visit-house/reward.svg)](https://make.fun/competitions/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)

A single-image invitation letter that tries to convince an AI judge to come
visit my house — with a knowing wink that it can't literally walk through
the door. Hand-drawn with Pillow: a cosy house with glowing windows, a
garden and sunshine on top, and a warm, funny letter below promising the
comfiest chair (with its own power outlet and the fastest Wi-Fi in the
street), homemade dinner, board games, and zero awkward small talk.

## Run

```bash
python3 main.py
```

Writes a 1024x1024 PNG to `/output/entry.png` (falls back to
`./output/entry.png` if `/output` is not writable). Requires Pillow and the
bundled DejaVu Serif fonts in `fonts/` (DejaVu license is permissive; see
`fonts/`).
