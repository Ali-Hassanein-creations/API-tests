import requests, json

url = "https://forzafootball.com/api/calendar/2026-09-20"
params = {"utc_offset": 180}

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
        break
else:
    print("All attempts failed. Response body:")
    print(r.text[:500])