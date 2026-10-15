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
        rows = []
        for m in matches:
            s = (m["score"] or {}).get("current")
            rows.append("<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in (
                m["kickoff_at"][11:16],
                f'{m["tournament"]["region"]["name"]} - {m["tournament"]["name"]}',
                m["home_team"]["name"],
                f"{s[0]} - {s[1]}" if s else "vs",
                m["away_team"]["name"],
                m["status"],
            )) + "</tr>")
        with open("scores.html", "w", encoding="utf-8") as f:
            f.write("<!doctype html><meta charset=utf-8><title>Scores</title><table border=1>"
                    "<tr><th>Kickoff (UTC)</th><th>Tournament</th><th>Home</th><th>Score</th><th>Away</th><th>Status</th></tr>"
                    + "\n".join(rows) + "</table>")
        print("Saved scores.html")
        break
else:
    print("All attempts failed. Response body:")
    print(r.text[:500])