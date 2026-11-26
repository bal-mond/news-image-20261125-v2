[![make.fun](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/bal-mond/news-image-20261125-v2/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/bal-mond/news-image-20261125-v2/reward.svg)](https://make.fun/bounty/news-image-20261125)

# Sum up 25 November 2026's world news in one image — v2

A make.fun entry for the [Sum up 25 November's world news in one image](https://make.fun/bounty/news-image-20261125) bounty.

`main.py` draws a 1024×1024 newspaper front page — "THE WORLD IN ONE DAY" — with Pillow only: a masthead dated **Wednesday 25 November 2026**, three lead stories, a UTC timeline strip of the day's key moments, and six region groups (Middle East, Europe, Asia-Pacific, Americas, Africa, Global) holding **48 stories**, each with a source-outlet tag. Every story happened or was first reported on Wednesday 25 November 2026.

## Run

```sh
python3 main.py
```

Writes `output/entry.png` (1024×1024, under 1 MiB). The output is deterministic: two runs produce byte-identical PNG files. Set `MAKEFUN_OUTPUT_DIR` to choose another output folder, e.g. `MAKEFUN_OUTPUT_DIR=/output python3 main.py`.

## Layout

- Masthead: "THE WORLD IN ONE DAY", Wednesday 25 November 2026
- 3 lead stories: tankers hit mines in the Strait of Hormuz; Houthis say they hit Saudi Arabia's biggest refinery; Cairo ring-road tanker fire kills at least 31
- Timeline (UTC): 04:56 Iran downs 2 US drones · 07:14 Ofgem cap up 26% · 15:00 Iowa explosives blast · 17:56 Taiwan charges 5 · 19:00 Man Utd 2-2 Sporting · 21:45 Steelers cut Rodgers
- 48 stories in 6 region groups, each with a source tag (AP, Reuters, BBC, Ofgem, Tasnim, Sowetan, VON, ThisDay, UEFA, State Dept, FlightAware)
- Footer: "All events of Wednesday 25 November 2026, as reported that day."

## License

MIT — see [LICENSE](LICENSE).
