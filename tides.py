import datetime as dt
from astral import LocationInfo
from astral.sun import sun

# Source: temperaturadomar.pt tide predictions for Jijoca de Jericoacoara (BRT, UTC-3).
# Format per day: list of (time, height_m, 'H'|'L'). Oct 7 and Dec 1 included so
# midway times at the edges can be computed.
RAW = """
2026-10-07 H 02:08 3.01 L 08:24 0.63 H 14:40 2.98 L 20:41 0.70
2026-10-08 H 02:55 3.17 L 09:06 0.52 H 15:21 3.15 L 21:24 0.53
2026-10-09 H 03:37 3.25 L 09:44 0.45 H 15:58 3.25 L 22:03 0.42
2026-10-10 H 04:16 3.27 L 10:20 0.44 H 16:33 3.29 L 22:40 0.38
2026-10-11 H 04:53 3.21 L 10:54 0.48 H 17:06 3.26 L 23:15 0.40
2026-10-12 H 05:28 3.10 L 11:26 0.57 H 17:39 3.17 L 23:50 0.47
2026-10-13 H 06:03 2.94 L 11:58 0.69 H 18:11 3.05
2026-10-14 L 00:25 0.59 H 06:37 2.76 L 12:31 0.84 H 18:45 2.89
2026-10-15 L 01:03 0.75 H 07:15 2.58 L 13:07 1.00 H 19:22 2.73
2026-10-16 L 01:44 0.92 H 07:58 2.40 L 13:49 1.17 H 20:07 2.56
2026-10-17 L 02:36 1.09 H 08:55 2.25 L 14:43 1.34 H 21:08 2.41
2026-10-18 L 03:43 1.22 H 10:16 2.17 L 15:59 1.44 H 22:32 2.34
2026-10-19 L 05:05 1.26 H 11:45 2.22 L 17:28 1.44 H 23:57 2.39
2026-10-20 L 06:20 1.19 H 12:52 2.36 L 18:40 1.32
2026-10-21 H 01:00 2.53 L 07:15 1.06 H 13:39 2.56 L 19:33 1.14
2026-10-22 H 01:48 2.71 L 07:57 0.90 H 14:17 2.77 L 20:15 0.92
2026-10-23 H 02:29 2.90 L 08:35 0.74 H 14:51 2.97 L 20:54 0.69
2026-10-24 H 03:07 3.06 L 09:11 0.58 H 15:25 3.16 L 21:32 0.48
2026-10-25 H 03:45 3.19 L 09:48 0.47 H 16:01 3.31 L 22:11 0.30
2026-10-26 H 04:24 3.25 L 10:26 0.40 H 16:38 3.40 L 22:52 0.20
2026-10-27 H 05:06 3.24 L 11:06 0.41 H 17:19 3.41 L 23:36 0.19
2026-10-28 H 05:50 3.15 L 11:49 0.49 H 18:02 3.33
2026-10-29 L 00:23 0.28 H 06:39 2.99 L 12:36 0.64 H 18:51 3.19
2026-10-30 L 01:16 0.45 H 07:33 2.80 L 13:28 0.83 H 19:47 3.01
2026-10-31 L 02:16 0.66 H 08:38 2.62 L 14:31 1.02 H 20:55 2.83
2026-11-01 L 03:26 0.84 H 09:55 2.52 L 15:48 1.15 H 22:16 2.73
2026-11-02 L 04:46 0.93 H 11:17 2.53 L 17:12 1.16 H 23:38 2.73
2026-11-03 L 06:02 0.92 H 12:28 2.65 L 18:28 1.06
2026-11-04 H 00:48 2.81 L 07:04 0.85 H 13:25 2.81 L 19:29 0.91
2026-11-05 H 01:45 2.91 L 07:55 0.77 H 14:12 2.95 L 20:19 0.75
2026-11-06 H 02:33 2.98 L 08:38 0.70 H 14:53 3.07 L 21:02 0.62
2026-11-07 H 03:16 3.02 L 09:17 0.65 H 15:31 3.14 L 21:41 0.53
2026-11-08 H 03:55 3.02 L 09:53 0.64 H 16:07 3.16 L 22:18 0.49
2026-11-09 H 04:32 2.98 L 10:27 0.66 H 16:41 3.14 L 22:54 0.49
2026-11-10 H 05:07 2.91 L 11:00 0.71 H 17:14 3.09 L 23:29 0.53
2026-11-11 H 05:42 2.82 L 11:34 0.78 H 17:48 3.01
2026-11-12 L 00:04 0.62 H 06:17 2.71 L 12:09 0.88 H 18:23 2.90
2026-11-13 L 00:42 0.73 H 06:55 2.59 L 12:46 0.99 H 19:00 2.79
2026-11-14 L 01:22 0.86 H 07:36 2.48 L 13:27 1.12 H 19:43 2.66
2026-11-15 L 02:09 1.00 H 08:26 2.38 L 14:17 1.24 H 20:35 2.54
2026-11-16 L 03:03 1.11 H 09:27 2.32 L 15:17 1.34 H 21:38 2.46
2026-11-17 L 04:06 1.17 H 10:38 2.33 L 16:29 1.37 H 22:51 2.45
2026-11-18 L 05:12 1.17 H 11:45 2.42 L 17:39 1.30 H 23:59 2.51
2026-11-19 L 06:12 1.10 H 12:40 2.57 L 18:40 1.15
2026-11-20 H 00:57 2.64 L 07:04 0.98 H 13:26 2.75 L 19:31 0.94
2026-11-21 H 01:47 2.79 L 07:50 0.83 H 14:09 2.95 L 20:18 0.70
2026-11-22 H 02:33 2.94 L 08:34 0.69 H 14:50 3.14 L 21:04 0.47
2026-11-23 H 03:19 3.06 L 09:18 0.56 H 15:33 3.29 L 21:50 0.29
2026-11-24 H 04:05 3.14 L 10:03 0.48 H 16:18 3.40 L 22:37 0.18
2026-11-25 H 04:53 3.15 L 10:50 0.46 H 17:05 3.43 L 23:26 0.16
2026-11-26 H 05:42 3.11 L 11:38 0.50 H 17:54 3.40
2026-11-27 L 00:17 0.23 H 06:34 3.03 L 12:29 0.60 H 18:47 3.31
2026-11-28 L 01:11 0.37 H 07:29 2.91 L 13:24 0.74 H 19:44 3.16
2026-11-29 L 02:08 0.55 H 08:29 2.79 L 14:23 0.89 H 20:46 3.00
2026-11-30 L 03:10 0.73 H 09:33 2.71 L 15:30 1.01 H 21:53 2.85
2026-12-01 L 04:15 0.87 H 10:41 2.67 L 16:41 1.07 H 23:04 2.75
"""

TZ = dt.timezone(dt.timedelta(hours=-3))
START, END = dt.date(2026, 10, 8), dt.date(2026, 11, 30)


def parse():
    events = []
    for line in RAW.strip().splitlines():
        parts = line.split()
        d = dt.date.fromisoformat(parts[0])
        for i in range(1, len(parts), 3):
            kind, hm, h = parts[i], parts[i + 1], float(parts[i + 2])
            t = dt.datetime.combine(d, dt.time.fromisoformat(hm), tzinfo=TZ)
            events.append({"t": t, "h": h, "kind": kind})
    events.sort(key=lambda e: e["t"])
    # sanity: kinds must alternate
    for a, b in zip(events, events[1:]):
        assert a["kind"] != b["kind"], (a, b)
    return events


def build_days(events):
    loc = LocationInfo("Guriu", "Brazil", "America/Fortaleza", -2.816, -40.60)
    days = []
    d = START
    while d <= END:
        s = sun(loc.observer, date=d, tzinfo=TZ)
        sr, ss = s["sunrise"], s["sunset"]
        day_ev = [e for e in events if e["t"].date() == d]
        highs = [e["h"] for e in day_ev if e["kind"] == "H"]
        lows = [e["h"] for e in day_ev if e["kind"] == "L"]
        amp = max(highs) - min(lows)
        # timeline: extremes + midway points between consecutive extremes, daytime only
        items = []
        for a, b in zip(events, events[1:]):
            mid_t = a["t"] + (b["t"] - a["t"]) / 2
            mid_h = (a["h"] + b["h"]) / 2
            direction = "rising" if b["kind"] == "H" else "falling"
            if sr <= mid_t <= ss:
                items.append({"t": mid_t, "h": mid_h, "kind": "M", "dir": direction})
        for e in day_ev:
            if sr <= e["t"] <= ss:
                items.append(dict(e))
        items.sort(key=lambda x: x["t"])
        w_start = dt.datetime.combine(d, dt.time(11, 0), tzinfo=TZ)
        w_end = dt.datetime.combine(d, dt.time(17, 0), tzinfo=TZ)
        sail = None
        for i, e in enumerate(events):
            if e["kind"] != "L" or e["t"].date() != d or not (0 < i < len(events) - 1):
                continue
            prev, nxt = events[i - 1], events[i + 1]
            m1 = prev["t"] + (e["t"] - prev["t"]) / 2   # falling mid
            m2 = e["t"] + (nxt["t"] - e["t"]) / 2       # rising mid
            a, b = max(m1, w_start), min(m2, w_end)
            if b - a >= dt.timedelta(hours=1) and e["h"] >= 0.5:
                sail = {"from": a, "to": b, "low": e}
        days.append({"date": d, "sunrise": sr, "sunset": ss, "amp": amp, "sail": sail,
                     "items": items, "min_low": min(lows), "max_high": max(highs)})
        d += dt.timedelta(days=1)
    return days


def color(amp, lo, hi):
    # green (hue 125) for the smallest amplitude -> red (hue 0) for the largest
    f = (amp - lo) / (hi - lo)
    hue = 125 * (1 - f)
    return f"hsl({hue:.0f} 62% 86%)", f"hsl({hue:.0f} 55% 34%)"


def render(days):
    lo = min(x["amp"] for x in days)
    hi = max(x["amp"] for x in days)
    months = {}
    for x in days:
        months.setdefault((x["date"].year, x["date"].month), []).append(x)

    def fmt(t):
        return t.strftime("%H:%M")

    cells_html = []
    for (y, m), ds in months.items():
        name = dt.date(y, m, 1).strftime("%B %Y")
        first = ds[0]["date"]
        pad = first.weekday()  # Monday = 0
        cells = ['<div class="cell pad"></div>'] * pad
        for x in ds:
            bg, fg = color(x["amp"], lo, hi)
            rows = []
            for it in x["items"]:
                if it["kind"] == "H":
                    rows.append(f'<li class="hi"><span>{fmt(it["t"])}</span><b>HIGH</b><i>{it["h"]:.2f} m</i></li>')
                elif it["kind"] == "L":
                    rows.append(f'<li class="lo"><span>{fmt(it["t"])}</span><b>LOW</b><i>{it["h"]:.2f} m</i></li>')
                else:
                    arrow = "&#8599;" if it["dir"] == "rising" else "&#8600;"
                    rows.append(f'<li class="mid"><span>{fmt(it["t"])}</span><b>mid {arrow}</b><i>{it["h"]:.2f} m</i></li>')
            sail = x["sail"]
            cls = "cell sail" if sail else "cell"
            sail_html = (f'<div class="win">sail {fmt(sail["from"])}&ndash;{fmt(sail["to"])}</div>' if sail else "")
            cells.append(
                f'<div class="{cls}" style="--bg:{bg};--fg:{fg}">'
                f'<div class="head"><span class="dnum">{x["date"].day}</span>'
                f'<span class="amp">{x["amp"]:.2f} m</span></div>'
                f'<div class="sun">&#9728; {fmt(x["sunrise"])} &ndash; {fmt(x["sunset"])}</div>{sail_html}'
                f'<ul>{"".join(rows)}</ul></div>'
            )
        cells_html.append(f'<h2>{name}</h2><div class="grid">'
                          '<div class="wd">Mon</div><div class="wd">Tue</div><div class="wd">Wed</div>'
                          '<div class="wd">Thu</div><div class="wd">Fri</div><div class="wd">Sat</div>'
                          '<div class="wd">Sun</div>' + "".join(cells) + "</div>")

    best = sorted(days, key=lambda x: x["amp"])[:6]
    worst = sorted(days, key=lambda x: -x["amp"])[:6]
    def daylist(ds):
        return ", ".join(f'{x["date"].strftime("%-d %b")} ({x["amp"]:.2f} m)' for x in ds)

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Guriú tide calendar – 8 Oct to 30 Nov 2026</title>
<style>
:root {{ --ink:#1c2a33; --muted:#5c6b74; --line:#d9dde0; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; padding:28px 24px 48px; background:#fbfbf9; color:var(--ink);
  font-family:"Avenir Next","Segoe UI",Helvetica,Arial,sans-serif; font-size:14px; line-height:1.35; }}
header {{ max-width:1180px; margin:0 auto 22px; }}
h1 {{ font-size:26px; font-weight:600; margin:0 0 6px; letter-spacing:-.01em; }}
h2 {{ font-size:19px; font-weight:600; margin:30px 0 10px; }}
p {{ margin:4px 0; color:var(--muted); max-width:78ch; }}
.scale {{ display:flex; align-items:center; gap:10px; margin:14px 0 4px; color:var(--muted); }}
.scale .bar {{ height:12px; width:260px; border-radius:6px;
  background:linear-gradient(90deg,hsl(125 62% 86%),hsl(62 62% 86%),hsl(0 62% 86%)); border:1px solid var(--line); }}
main {{ max-width:1180px; margin:0 auto; }}
.grid {{ display:grid; grid-template-columns:repeat(7,1fr); gap:6px; }}
.wd {{ color:var(--muted); font-size:12px; padding:0 4px 4px; }}
.cell {{ background:#fff; border:1px solid var(--line); border-radius:8px; padding:8px 9px 9px; min-height:150px; }}
.cell.pad {{ background:transparent; border:none; }}
.cell.sail {{ outline:3px solid #1e9e4a; outline-offset:-1px; }}
.win {{ font-size:12px; font-weight:600; color:#187a3a; margin:-2px 0 6px; }}
.legend {{ display:flex; align-items:center; gap:10px; margin:10px 0 4px; color:var(--muted); }}
.legend .box {{ width:34px; height:22px; border:1px solid var(--line); border-radius:6px; outline:3px solid #1e9e4a; outline-offset:-1px; background:#fff; }}
.head {{ display:flex; justify-content:space-between; align-items:baseline; }}
.dnum {{ font-size:18px; font-weight:600; }}
.amp {{ font-size:12.5px; font-weight:600; color:var(--fg); background:var(--bg); padding:2px 8px; border-radius:999px; }}
.sun {{ font-size:11px; color:var(--muted); margin:2px 0 6px; }}
ul {{ list-style:none; margin:0; padding:0; }}
li {{ display:grid; grid-template-columns:44px 1fr auto; gap:6px; font-size:12.5px; padding:1px 0; font-variant-numeric:tabular-nums; }}
li span {{ font-weight:600; }}
li i {{ font-style:normal; color:var(--muted); }}
li.hi b {{ font-weight:600; }}
li.lo b {{ font-weight:700; }}
li.mid {{ color:var(--muted); }}
li.mid b {{ font-weight:500; }}
.notes {{ max-width:1180px; margin:34px auto 0; }}
.notes ul {{ padding-left:18px; list-style:disc; color:var(--muted); }}
.notes li {{ display:list-item; font-size:13.5px; margin:3px 0; }}
@media (max-width:900px) {{ .grid {{ grid-template-columns:repeat(2,1fr); }} .wd {{ display:none; }} .cell.pad {{ display:none; }} }}
</style></head><body>
<header>
<h1>Guriú / Jericoacoara tides – 8 Oct to 30 Nov 2026</h1>
<p>Daylight tide events only (sunrise to sunset, local time UTC−3). Each day is shaded by its tidal amplitude
(highest high minus lowest low that day): green = smallest range, red = largest range.
"mid" rows are the halfway points between consecutive high and low water – the arrow shows whether the water is rising or falling.</p>
<div class="scale"><span>{lo:.2f} m</span><div class="bar"></div><span>{hi:.2f} m</span></div>
<div class="legend"><div class="box"></div><span>Green outline = potentially sailable: the mid&#8600; low &#8599;mid window overlaps 11:00&ndash;17:00 by at least an hour and the low water is 0.50 m or higher (below that the window is too short and the low too dry to sail). The "sail" line in the cell is that overlap.</span></div>
<p>Smallest ranges: {daylist(best)}.</p>
<p>Largest ranges: {daylist(worst)}.</p>
</header>
<main>{"".join(cells_html)}</main>
<section class="notes">
<h2>Notes</h2>
<ul>
<li>Predictions are for Jijoca de Jericoacoara (2°47′S 40°31′W); Guriú lies ~10 km west on the same open coast, so times differ by only a few minutes.</li>
<li>Heights are relative to the local chart datum (lowest astronomical tide); a "0.2 m" low means very little water.</li>
<li>Source: temperaturadomar.pt harmonic predictions, cross-checked against tabuademares.com. These are not the official DHN (Brazilian Navy) tables – verify against the Camocim table before relying on exact minutes.</li>
<li>Wind, swell and atmospheric pressure can shift real water levels by 10–30 cm and the timing by tens of minutes.</li>
</ul>
</section>
</body></html>"""
    return html


if __name__ == "__main__":
    ev = parse()
    days = build_days(ev)
    import os
    pass
    with open("index.html", "w") as f:
        f.write(render(days))
    # also a CSV
    with open("tides.csv", "w") as f:
        f.write("date,amplitude_m,sunrise,sunset,sailable_from,sailable_to,time,event,height_m\n")
        for x in days:
            for it in x["items"]:
                k = {"H": "high", "L": "low", "M": "mid-" + it.get("dir", "")}[it["kind"]]
                sf = f'{x["sail"]["from"]:%H:%M}' if x["sail"] else ""
                st = f'{x["sail"]["to"]:%H:%M}' if x["sail"] else ""
                f.write(f'{x["date"]},{x["amp"]:.2f},{x["sunrise"]:%H:%M},{x["sunset"]:%H:%M},{sf},{st},{it["t"]:%H:%M},{k},{it["h"]:.2f}\n')
    for x in days[:3]:
        print(x["date"], f'{x["amp"]:.2f}', x["sunrise"].strftime("%H:%M"), x["sunset"].strftime("%H:%M"),
              [(i["t"].strftime("%H:%M"), i["kind"], round(i["h"], 2)) for i in x["items"]])
    print("min", min(d["amp"] for d in days), "max", max(d["amp"] for d in days))
