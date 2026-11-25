# The World Today — 26 November 2026 in One Image

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/zws0a929/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/zws0a929/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A newspaper front page — **THE WORLD TODAY, Thursday, November 26, 2026** — that sums up the day's world news in a single 1024×1024 image.

## What the front page covers

- **Pakistan's first astronaut reaches China's space station** — Muhammad Zeeshan Ali flies aboard Shenzhou-24 and becomes the first foreign astronaut to board Tiangong.
- **Pyongyang expels the Swiss envoy** — North Korea orders Sylvain Astier out within 48 hours and closes the Swiss diplomatic office over sanctions on the Songdowon children's camp.
- **Hodeida hit, Houthis vow revenge** — the Saudi-led coalition strikes Yemen's port city; the Houthis threaten Jeddah and other Red Sea ports.
- **All 20 hostages freed in Cartagena** — Colombian forces storm an Exito supermarket after a 17-hour siege; one captor killed.
- **Pacific pact: Solomons choose Canberra** — Australia and Solomon Islands sign a landmark treaty (A$740 million over a decade); no foreign military bases on the islands.
- **Leaked figures put Russian war dead near 500,000** — Russia's own Rosstat data shows at least 490,334 soldiers killed in Ukraine.
- **Shanghai party chief under investigation** — Politburo member Chen Jining is probed for graft, the fourth top leader to fall since 2025.
- **Also:** the U.S. proposes new tariffs on 14 trading partners, with China facing the highest rate.

## How to run

```sh
python3 main.py               # copies entry.png to /output/entry.png
python3 main.py --verify-only # checks the image without writing a copy
```

`main.py` (Python 3.13, standard library only, no network) verifies the image — PNG signature, IHDR dimensions (1024×1024), IHDR CRC-32, 1 MiB size cap — then copies it byte for byte and confirms the copy with SHA-256, including a determinism self-check. It fails loudly if `entry.png` is missing.

## License

MIT License — see [LICENSE](LICENSE).

<sub>Entered on [make.fun](https://make.fun/?ref=81228bnq&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
