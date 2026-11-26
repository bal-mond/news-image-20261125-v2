#!/usr/bin/env python3
"""Sum up Wednesday 25 November 2026's world news in one image.

Draws a 1024x1024 newspaper front page with Pillow only: a masthead, three
lead stories, a UTC timeline strip of the day's key moments, and six region
groups holding 48 verified stories, each with a source-outlet tag.

Deterministic: no clock, no randomness, no network. Two runs write
byte-identical PNG bytes.

Usage:
    MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024

PAPER = (250, 246, 238)
CARD = (255, 255, 255)
INK = (22, 22, 22)
MUTED = (96, 92, 86)
RULE = (180, 172, 158)
RED = (178, 32, 44)
NAVY = (24, 38, 66)
NAVY_DECK = (216, 222, 233)
GOLD = (232, 184, 75)
TAG = (178, 32, 44)

FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts",
]


def load_font(bold, size):
    names = ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf"] if bold else [
        "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"]
    if bold:
        names = ["DejaVuSans-Bold.ttf"]
    else:
        names = ["DejaVuSans.ttf"]
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    for d in FONT_DIRS:
        for root, _dirs, files in os.walk(d):
            for f in files:
                if f.lower().endswith(".ttf") and ("sans" in f.lower()):
                    try:
                        return ImageFont.truetype(os.path.join(root, f), size)
                    except OSError:
                        continue
    return ImageFont.load_default(size=size)


def load_serif_bold(size):
    for d in FONT_DIRS:
        p = os.path.join(d, "DejaVuSerif-Bold.ttf")
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return load_font(True, size)


class Fonts:
    def __init__(self):
        self.title = load_serif_bold(34)
        self.date = load_font(True, 17)
        self.kicker = load_font(True, 10)
        self.lead_head = load_font(True, 14)
        self.lead_deck = load_font(False, 10)
        self.lead_tag = load_font(True, 9)
        self.tl_label = load_font(True, 9)
        self.tl_time = load_font(True, 10)
        self.tl_text = load_font(False, 9)
        self.region = load_font(True, 12)
        self.region_count = load_font(False, 9)
        self.head = load_font(True, 11)
        self.deck = load_font(False, 9)
        self.footer = load_font(False, 11)


def text_w(font, s):
    return font.getlength(s)


def wrap_text(draw, text, font, width, max_lines):
    """Greedy wrap to at most max_lines lines; ellipsis on the last line."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(font, trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and text_w(font, last + "\u2026") > width:
            last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
        lines[-1] = last + "\u2026" if last else "\u2026"
    return lines


def fit_line(draw, text, font, width):
    """Single line, truncated with ellipsis to fit width."""
    if text_w(font, text) <= width:
        return text
    s = text
    while s and text_w(font, s + "\u2026") > width:
        s = s.rsplit(" ", 1)[0] if " " in s else s[:-1]
    return s + "\u2026" if s else "\u2026"


# ---------------------------------------------------------------- stories
# (headline, deck, source) -- every story happened or was first reported
# on Wednesday 25 November 2026.

ME = [
    ("Tankers hit mines in the Strait of Hormuz",
     "Two oil tankers hit mines and catch fire.",
     "Reuters"),
    ("Houthis say they hit Saudi Arabia's biggest refinery",
     "Smoke seen over 600 sq km; four drones intercepted.",
     "Reuters"),
    ("Israel kills Hamas colonel in Gaza",
     "Mohammad Abuelouf killed with wife and two children.",
     "AP"),
    ("Iran claims it downed two US drones",
     "MQ-9 and Lucas drone downed, army says; US silent.",
     "Tasnim"),
    ("Judges urge dropping Netanyahu bribery case",
     "Judges tell prosecutors to drop the bribery case.",
     "AP"),
    ("Fuel tanker fire on Cairo ring road kills at least 31",
     "Crash and fire on Cairo ring road kills 31, injures 21.",
     "AP"),
    ("Brent crude closes at $94.61",
     "Oil up 3.5% after the Middle East attacks.",
     "Reuters"),
]

EUROPE = [
    ("Russian strike kills two in Odesa region",
     "Two killed, three hurt; Kyiv block hit, two injured.",
     "Reuters"),
    ("Leaked figures put Russian war dead at 490,334",
     "BBC-analysed leaked figures put toll near 500,000.",
     "BBC"),
    ("Poland plans no-fly zone on eastern border",
     "Warsaw moves to seal its eastern border airspace.",
     "Reuters"),
    ("France urges Putin to drop 'delusion'",
     "Paris presses Moscow to abandon its war aims.",
     "Reuters"),
    ("UK watchdog issues AI warning",
     "Regulator warns on AI as Meta launches adapted Muse.",
     "Reuters"),
    ("Strikes disrupt Eurostar trains",
     "Walkouts hit cross-Channel services.",
     "AP"),
    ("Boehly group agrees to buy Lukoil assets",
     "Deal struck for the Russian oil firm's overseas assets.",
     "Reuters"),
    ("UK energy price cap to rise 26%",
     "Typical bill \u00a32,166 from January, up \u00a3443 a year.",
     "Ofgem"),
    ("Duran Duran guitarist Andy Taylor dies at 65",
     "Band announces his death after prostate cancer.",
     "AP"),
    ("Fernandes rescues Man Utd in 2-2 draw at Sporting",
     "Two goals in three minutes; Suarez levels late.",
     "AP"),
    ("Liverpool hit Club Brugge 3-0",
     "Reds cruise in the Champions League on Wednesday.",
     "UEFA"),
]

ASIA_PACIFIC = [
    ("North Korean vessel watched near sea border",
     "Vessel labelled 'coast guard' near the Limit Line.",
     "Reuters"),
    ("Solomon Islands bars foreign bases",
     "Treaty with Australia bars foreign military bases.",
     "Reuters"),
    ("Shenzhou-24 docks, first Pakistani aboard",
     "Pakistan's first astronaut reaches the space station.",
     "AP"),
    ("Death sentence for leaking state secrets",
     "Official sentenced after leaking 100+ secrets.",
     "AP"),
    ("Garment wage rises 36% to $139",
     "Bangladesh raises pay for garment workers.",
     "Reuters"),
    ("Nine dead in West Java gold mine flood",
     "Illegal shaft floods in Bogor; 17 miners trapped.",
     "AP"),
    ("How China got Nvidia's AI chips despite rules",
     "Restricted chips reached Chinese data centres.",
     "Reuters"),
    ("Taiwan charges five over plot to attack comedian",
     "Plot to break comic's legs over Xi jokes, police say.",
     "Reuters"),
]

AMERICAS = [
    ("All 76 supermarket hostages freed",
     "Cartagena siege ends with all hostages freed.",
     "AP"),
    ("US drones help capture 'El Chapo Isidro'",
     "Cartel figure seized with US drone help.",
     "AP"),
    ("Second judge blocks birthright order",
     "Another court halts the birthright order.",
     "AP"),
    ("US economy roars; inflation stays high",
     "Q3 growth roars; October inflation stays high.",
     "AP"),
    ("Wall Street falls, then recovers",
     "Stocks dip on AI worries, then recover.",
     "Reuters"),
    ("CIA and spy chief's office breached",
     "Unclassified information taken in a cyber breach.",
     "Reuters"),
    ("Abrego Garcia lands in Spain",
     "Migrant arrives in Madrid after leaving the US.",
     "AP"),
    ("Steelers release Aaron Rodgers",
     "MVP cut hours after ripping coach McCarthy on TV.",
     "AP"),
    ("Army blows up 5 tons of unstable explosive",
     "Iowa detonation of ageing lead azide succeeds.",
     "Reuters"),
    ("Canada's student caps hit universities",
     "Permit cuts squeeze colleges and talent drive.",
     "Reuters"),
    ("Suriname marks 51 years of independence",
     "US and India greet the 25 November anniversary.",
     "State Dept"),
    ("Storms snarl Thanksgiving travel",
     "Nor'easter and 1,100+ delays hit US travel.",
     "FlightAware"),
]

AFRICA = [
    ("Drone strikes kill 19 civilians",
     "RSF strikes kill 19, wound 20 in two cities.",
     "AP"),
    ("Ebola workers evacuated from fighting",
     "UN pulls 10 Ebola workers out of eastern Congo.",
     "AP"),
    ("Nigeria seizes over $200m of meth",
     "Five Mexicans arrested in record drug haul.",
     "AP"),
    ("Ramaphosa wins Phala Phala court battle",
     "Court scraps report behind impeachment inquiry.",
     "Sowetan"),
    ("Nollywood legend Pete Edochie dies at 79",
     "Actor famed as Okonkwo dies in Enugu.",
     "VON"),
    ("Gunmen fire on rally in Benin City",
     "One hurt as shots hit Peter Obi supporters.",
     "ThisDay"),
]

GLOBAL = [
    ("Pope laments failure of COP31 talks",
     "Pope Leo XIV decries the collapse of climate talks.",
     "Reuters"),
    ("US famine monitor to halt reporting",
     "Funding shortfall ends famine early-warning reports.",
     "Reuters"),
    ("US proposes tariffs on 14 partners",
     "20% on China, 15% on EU, 10% on Brazil aircraft.",
     "Reuters"),
    ("Airports turn to private cash for upgrades",
     "$4tn of work ahead as private money funds terminals.",
     "Reuters"),
]

REGIONS = [
    ("MIDDLE EAST", (140, 47, 57), ME),
    ("EUROPE", (31, 78, 121), EUROPE),
    ("ASIA-PACIFIC", (30, 107, 82), ASIA_PACIFIC),
    ("AMERICAS", (122, 74, 18), AMERICAS),
    ("AFRICA", (91, 58, 117), AFRICA),
    ("GLOBAL", (68, 84, 106), GLOBAL),
]

LEADS = [ME[0], ME[1], ME[5]]

# Fuller decks used only in the three lead boxes (2 lines each).
LEAD_DECKS = [
    "Two oil tankers struck naval mines and caught fire; Iran's Guard blames an unauthorised route.",
    "Satellite images show smoke over 600 sq km; the Saudi-led coalition says four drones were intercepted.",
    "A fuel tanker crash and fire on the ring road around Cairo kills at least 31 people and injures 21.",
]

TIMELINE = [
    ("04:56", "Iran downs 2 US drones"),
    ("07:14", "Ofgem: cap up 26%"),
    ("15:00", "Iowa: 5t explosives blast"),
    ("17:56", "Taiwan: 5 charged"),
    ("19:00", "Man Utd 2-2 Sporting"),
    ("21:45", "Steelers cut Rodgers"),
]

FOOTER = "All events of Wednesday 25 November 2026, as reported that day."


def story_block_height(draw, fonts, story, width, head_size, deck_size):
    head_f = load_font(True, head_size)
    lines = wrap_text(draw, story[0], head_f, width, 2)
    lh = head_size + 2
    return len(lines) * lh + deck_size + 5


def draw_story(draw, fonts, story, x, y, width, head_size, deck_size):
    head_f = load_font(True, head_size)
    deck_f = load_font(False, deck_size)
    tag_f = load_font(True, deck_size)
    lines = wrap_text(draw, story[0], head_f, width, 2)
    lh = head_size + 2
    cy = y
    for ln in lines:
        draw.text((x, cy), ln, font=head_f, fill=INK)
        cy += lh
    tag = "  \u00b7  " + story[2]
    tag_w = text_w(tag_f, tag)
    deck = fit_line(draw, story[1], deck_f, width - tag_w)
    draw.text((x, cy), deck, font=deck_f, fill=MUTED)
    draw.text((x + text_w(deck_f, deck), cy), tag, font=tag_f, fill=TAG)
    return cy + deck_size + 5


def draw_page():
    fonts = Fonts()
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    margin = 14
    gutter = 10
    col_w = 325
    xs = [margin, margin + col_w + gutter, margin + 2 * (col_w + gutter)]
    content_w = 3 * col_w + 2 * gutter  # 995

    # ---- masthead ------------------------------------------------------
    y = 12
    d.text((margin, y), "THE WORLD IN ONE DAY", font=fonts.title, fill=INK)
    date_w = text_w(fonts.date, "Wednesday 25 November 2026")
    d.text((margin + content_w - date_w, y + 8),
           "Wednesday 25 November 2026", font=fonts.date, fill=RED)
    y += 46
    kicker = "48 STORIES  \u00b7  SIX REGIONS  \u00b7  ONE DAY"
    d.text((margin, y), kicker, font=fonts.kicker, fill=MUTED)
    count = "25 NOV 2026"
    d.text((margin + content_w - text_w(fonts.kicker, count), y),
           count, font=fonts.kicker, fill=MUTED)
    y += 18
    d.line([(margin, y), (margin + content_w, y)], fill=INK, width=2)
    d.line([(margin, y + 3), (margin + content_w, y + 3)], fill=RULE, width=1)
    y += 10

    # ---- lead boxes ----------------------------------------------------
    lead_h = 102
    lead_top = y
    for i, story in enumerate(LEADS):
        x = xs[i]
        d.rectangle([x, lead_top, x + col_w, lead_top + lead_h], fill=NAVY)
        d.rectangle([x, lead_top, x + 4, lead_top + lead_h], fill=RED)
        ix = x + 12
        iw = col_w - 24
        d.text((ix, lead_top + 7), "LEAD STORY", font=fonts.lead_tag,
               fill=GOLD)
        lines = wrap_text(d, story[0], fonts.lead_head, iw, 2)
        cy = lead_top + 22
        for ln in lines:
            d.text((ix, cy), ln, font=fonts.lead_head, fill=(255, 255, 255))
            cy += 17
        deck_lines = wrap_text(d, LEAD_DECKS[i], fonts.lead_deck, iw, 2)
        for ln in deck_lines:
            d.text((ix, cy), ln, font=fonts.lead_deck, fill=NAVY_DECK)
            cy += 13
        tag = "Source: " + story[2]
        d.text((ix, lead_top + lead_h - 16), tag, font=fonts.lead_tag,
               fill=GOLD)
    y = lead_top + lead_h + 8

    # ---- UTC timeline --------------------------------------------------
    tl_top = y
    d.text((margin, tl_top), "THE DAY IN UTC",
           font=fonts.tl_label, fill=RED)
    d.text((margin + content_w - text_w(fonts.tl_label, "ALL TIMES UTC"),
            tl_top), "ALL TIMES UTC", font=fonts.tl_label, fill=MUTED)
    line_y = tl_top + 28
    d.line([(margin + 8, line_y), (margin + content_w - 8, line_y)],
           fill=RULE, width=2)
    n = len(TIMELINE)
    span = content_w - 40
    for i, (t, label) in enumerate(TIMELINE):
        cx = margin + 20 + int(i * span / (n - 1))
        d.ellipse([cx - 5, line_y - 5, cx + 5, line_y + 5],
                  fill=RED, outline=(255, 255, 255), width=1)
        tw = text_w(fonts.tl_time, t)
        d.text((cx - tw / 2, line_y - 18), t, font=fonts.tl_time, fill=INK)
        # One short line per moment, centred on its dot and clamped
        # inside the page margins so neighbours never touch.
        lab = fit_line(d, label, fonts.tl_text, 170)
        lw = text_w(fonts.tl_text, lab)
        lx = min(max(cx - lw / 2, margin), margin + content_w - lw)
        d.text((lx, line_y + 9), lab, font=fonts.tl_text, fill=MUTED)
    y = tl_top + 58

    # ---- region groups -------------------------------------------------
    # Two rows of three groups; each group's height fits its stories.
    head_size, deck_size = 11, 9
    pad = 8
    header_h = 24
    rows = [REGIONS[0:3], REGIONS[3:6]]
    for row in rows:
        heights = []
        for _name, _color, stories in row:
            total = header_h + pad
            for s in stories:
                total += story_block_height(d, fonts, s, col_w - 2 * pad,
                                            head_size, deck_size)
            total += pad
            heights.append(total)
        row_h = max(heights)
        for j, (name, color, stories) in enumerate(row):
            x = xs[j]
            d.rectangle([x, y, x + col_w, y + row_h], fill=CARD,
                        outline=color, width=1)
            d.rectangle([x, y, x + col_w, y + header_h], fill=color)
            d.text((x + pad, y + 5), name, font=fonts.region,
                   fill=(255, 255, 255))
            cnt = "%d stories" % len(stories)
            d.text((x + col_w - pad - text_w(fonts.region_count, cnt),
                    y + 7), cnt, font=fonts.region_count,
                   fill=(230, 230, 230))
            sy = y + header_h + pad
            for s in stories:
                sy = draw_story(d, fonts, s, x + pad, sy,
                                col_w - 2 * pad, head_size, deck_size)
        y += row_h + 8

    # ---- footer --------------------------------------------------------
    fw = text_w(fonts.footer, FOOTER)
    d.text(((W - fw) / 2, H - 22), FOOTER, font=fonts.footer, fill=INK)
    d.line([(margin, H - 30), (margin + content_w, H - 30)],
           fill=RULE, width=1)
    return img, y


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "output"
    os.makedirs(out_dir, exist_ok=True)
    img, regions_end = draw_page()
    print("regions end at y=%d (footer rule at y=%d)" % (regions_end, H - 30))
    path = os.path.join(out_dir, "entry.png")
    img.save(path, "PNG")
    size = os.path.getsize(path)
    print("wrote %s (%d bytes)" % (path, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
