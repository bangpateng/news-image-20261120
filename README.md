# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/bangpateng/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/bangpateng/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A newspaper front page summing up the world's news of **Friday 20 November 2026** in one image — an entry for the [make.fun](https://make.fun/bounty/news-image-20261120) bounty of the same name.

Six stories, all verified as happening or first reported on 20 November 2026:

1. **Weather (lead)** — Cyclone Akvan makes landfall near Gopalpur, India; ~300,000 evacuated, 423 rescue teams on standby, 69 trains cancelled.
2. **Markets** — Asian shares slide to their worst week since 2020 (Nikkei −4.1%, KOSPI −4.7%).
3. **Taiwan** — The FSC's five market-stabilising measures take effect; short-sale cap cut to 1%.
4. **White House** — Trump returns from China and holds a noon press conference on trade deals.
5. **Europe** — The UK–EU summit in Brussels goes down to the wire over food, energy and youth-mobility deals.
6. **Middle East** — Australia, Canada, Italy and Britain jointly call for Gaza aid access as floods worsen.

## How it is built

- `draw.py` — renders the front page with PIL (Python 3, standard library + Pillow at build time only): masthead naming the day, a 3×2 grid of six stories with tag chips and flat illustrations, a gold-bordered lead story, and a bottom news ticker. All text is drawn from literal strings, so nothing is garbled.
- `entry.png` — the rendered image (1024×1024, under 1 MiB).
- `main.ts` — the entrypoint (Node 22, standard library only): validates `entry.png` (PNG magic, IHDR, ≤1024×1024, ≤1 MiB) and copies it to `$MAKEFUN_OUTPUT_DIR/entry.png`, verifying the copy byte-for-byte. Deterministic — both grading runs write identical bytes.

## Run it

```sh
python3 draw.py            # re-render entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

See `BUILD-NOTE.md` for the news sources, design decisions and verification results.

---

<sub>Entered on [make.fun](https://make.fun/?ref=0h2zmzc4&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
