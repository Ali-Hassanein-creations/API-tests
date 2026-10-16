import requests, json, html
from datetime import date, datetime

url = f"https://forzafootball.com/api/calendar/{date.today()}"
params = {"utc_offset": int(datetime.now().astimezone().utcoffset().total_seconds() // 60)}

base = {
    "accept": "*/*",
    "accept-language": "en",
    "referer": "https://forzafootball.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36",
}
sec = {
    "sec-ch-ua": '"Brave";v="153", "Not_A Brand";v="8", "Chromium";v="153"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}
country = {"x-client-country": "KW"}
cookies = {"NEXT_COUNTRY": "KW", "ff_lang": "en", "ff_country": "US"}  # preference cookies only

attempts = [
    ("base", base, {}),
    ("+sec headers", {**base, **sec}, {}),
    ("+country header", {**base, **sec, **country}, {}),
    ("+cookies", {**base, **sec, **country}, cookies),
]

for name, h, c in attempts:
    r = requests.get(url, params=params, headers=h, cookies=c, timeout=10)
    print(f"{name}: {r.status_code} | server={r.headers.get('server')}")
    if r.ok:
        data = r.json()
        with open("scores.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Saved scores.json")

        matches = sorted(data["matches"], key=lambda m: (m["tournament"]["priority"], m["kickoff_at"]))
        e = lambda v: html.escape(str(v))
        rows, last = [], None
        for m in matches:
            t = f'{m["tournament"]["region"]["name"]} · {m["tournament"]["name"]}'
            if t != last:
                rows.append(f'<tr class=group><th colspan=5>{e(t)}</th></tr>')
                last = t
            s = (m["score"] or {}).get("current")
            st = m["status"]
            rows.append(
                f'<tr><td class=time>{e(m["kickoff_at"][11:16])}</td>'
                f'<td class=home>{e(m["home_team"]["name"])}</td>'
                f'<td class="score {st}">{e(f"{s[0]} – {s[1]}" if s else "vs")}</td>'
                f'<td class=away>{e(m["away_team"]["name"])}</td>'
                f'<td><span class="badge {st}">{ {"before": "Upcoming", "live": "Live", "after": "FT"}.get(st, e(st)) }</span></td></tr>')
        title = f"Forza Football · Matches for {date.today():%A, %d %B %Y}"
        with open("scores.html", "w", encoding="utf-8") as f:
            f.write(f"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root{{--bg:#f4f6f8;--card:#fff;--text:#1a1f24;--muted:#6b7580;--line:#e3e7eb;--accent:#0a8f4e;--live:#d92d20}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0f1418;--card:#182027;--text:#e8edf1;--muted:#8a96a1;--line:#26313a;--accent:#2fd17f;--live:#ff5a4f}}}}
body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:820px;margin:0 auto;padding:32px 16px}}
h1{{margin:0 0 4px;font-size:26px}} h1 span{{color:var(--accent)}}
p{{margin:0 0 24px;color:var(--muted)}}
table{{width:100%;border-collapse:collapse;background:var(--card);border-radius:12px;overflow:hidden;box-shadow:0 1px 3px #0002}}
td,th{{padding:10px 12px;border-bottom:1px solid var(--line)}}
tr.group th{{text-align:left;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);background:var(--bg);padding-top:18px}}
tbody tr:not(.group):hover{{background:var(--bg)}}
.time{{color:var(--muted);font-variant-numeric:tabular-nums;width:52px}}
.home{{text-align:right;width:35%}} .away{{width:35%}}
.score{{text-align:center;font-weight:700;font-variant-numeric:tabular-nums;white-space:nowrap}}
.score.before{{color:var(--muted);font-weight:400}} .score.live{{color:var(--live)}}
.badge{{font-size:11px;font-weight:600;padding:3px 8px;border-radius:99px;background:var(--line);color:var(--muted);white-space:nowrap}}
.badge.live{{background:var(--live);color:#fff}} .badge.after{{color:var(--text)}}
@media (max-width:560px){{.time{{display:none}} td,th{{padding:8px 6px}}}}
</style>
<main><h1><span>⚽</span> {title}</h1><p>{len(matches)} matches · kickoff times in UTC</p>
<table><tbody>
""" + "\n".join(rows) + "\n</tbody></table></main>")
        print("Saved scores.html")
        break
else:
    print("All attempts failed. Response body:")
    print(r.text[:500])