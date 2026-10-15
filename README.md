# API Testing Notes — Forza Football Calendar Endpoint

## Objective
Determine what request headers/cookies are required to successfully call the
Forza Football calendar API from outside a browser (i.e. via a plain Python
script) and retrieve match data for a given date.

## Endpoint under test
```
GET https://forzafootball.com/api/calendar/{YYYY-MM-DD}
Query params: utc_offset={minutes}
```
The script fills in today's date and your machine's current UTC offset
(e.g. `180` for UTC+3), so the API returns *today's* matches in your local
day. Each run is a snapshot: re-run it to refresh live scores.

## Method
Script: [`import requests, json.py`](import%20requests%2C%20json.py)

The test used an **incremental header escalation** approach — starting from a
minimal request and adding groups of headers/cookies one at a time until the
request succeeded, in order to isolate which pieces of the request the API
actually requires:

| Step | Headers/cookies added | Purpose |
|------|------------------------|---------|
| 1. `base` | `accept`, `accept-language`, `referer`, `user-agent` | Minimal browser-like request |
| 2. `+sec headers` | `sec-ch-ua`, `sec-ch-ua-mobile`, `sec-ch-ua-platform`, `sec-fetch-dest`, `sec-fetch-mode`, `sec-fetch-site` | Client Hints / Fetch metadata that browsers send automatically and some APIs check for |
| 3. `+country header` | `x-client-country: KW` | Region/locale hint used by the site |
| 4. `+cookies` | `NEXT_COUNTRY`, `ff_lang`, `ff_country` (preference cookies only, no auth/session cookies) | Site locale preference cookies |

For each step, the script sent the request and printed the status code and
`server` response header, stopping at the first attempt that returned a
successful (`2xx`) response.

## Result
Step 1 (`base`) is rejected with `403` by CloudFront; step 2 (`+sec headers`)
returns `200`. The JSON body is saved to [`scores.json`](scores.json), and a
plain HTML table is written to `scores.html`.

### `scores.html`
One row per match, sorted by tournament priority (big leagues first), then
kickoff time. Columns: Kickoff (UTC), Tournament, Home, Score, Away, Status
(`before` / `live` / `after`). Matches not yet started show `vs`.

The response contains a `matches` array, where each match includes:
- `home_team` / `away_team` objects (`id`, `name`, `abbreviation`, `slug`,
  `region`, `age_group`, colors, etc.)
- `kickoff_at` (UTC timestamp) and `kickoff_time_tbd`
- `match_time` (normal length, current/added time)
- `score`, `red_card_count`, `attendance`, `indicators`, `disabled_features`,
  and live-match flags (`has_live_scores`, `has_videos`, `ongoing_var_review`)

## Takeaways
- No authentication token or session cookie was required — only a realistic
  `user-agent`/`referer` and standard browser metadata headers were enough to
  get past the API's basic request filtering.
- The cookies used were locale/preference cookies only (country/language),
  not auth cookies — confirming the endpoint is public read data, gated only
  on looking like a normal browser request.
- Only the `sec-*` Fetch metadata headers are actually required; the country
  header and cookies are never reached.
- The incremental approach makes it easy to identify the *minimal* working
  header set on a future run, by checking which numbered step first returns
  a `2xx` status.
