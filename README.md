# nlp_opinion_trend

Collect English posts + comments from Reddit and Twitter into a single CSV (`social_data.csv`) for NLP analysis.

## Setup

1) Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2) Create a Reddit API app:
- Go to `https://www.reddit.com/prefs/apps`
- Create an app (type: "script")

3) Set environment variables (Windows PowerShell):

```powershell
setx REDDIT_CLIENT_ID "YOUR_CLIENT_ID"
setx REDDIT_CLIENT_SECRET "YOUR_CLIENT_SECRET"
setx REDDIT_USER_AGENT "nlp_opinion_trend by u/YOUR_REDDIT_USERNAME"
```

Close and reopen your terminal so the environment variables are available.

## Run

Collect from one or more subreddits:

```bash
python get_data.py --subreddit news --subreddit worldnews --posts 30 --comments 30
```

Output file (default): `social_data.csv`

### Notes
- Reddit does not reliably expose user city/location. By default, the collector **simulates** the `city` field. Disable it with `--no-city-sim`.
- If you want posts only: `--no-comments`

