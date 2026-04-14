# nlp_opinion_trend

Collect English posts + comments from Reddit and Twitter into a single Excel file (`social_data.xlsx`) for NLP analysis.

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

## Run (env vars + constants)

Set configuration with environment variables, then run without arguments:

```powershell
$env:DATA_SOURCE="reddit"                # reddit | twitter | both
$env:SUBREDDITS="news,worldnews"         # comma-separated
$env:TWITTER_QUERIES="news,technology"   # comma-separated
$env:POSTS_LIMIT="30"
$env:COMMENTS_LIMIT="30"
$env:INCLUDE_COMMENTS="true"
$env:SIMULATE_CITY="true"
$env:OUTPUT_FILE="social_data.xlsx"
$env:DEBUG="false"
python get_data.py
```

Default output file: `social_data.xlsx`

### Kibana logging (optional)

You can stream logs to Elasticsearch (viewable in Kibana) by setting:

```powershell
$env:KIBANA_LOGGING_ENABLED="true"
$env:ELASTICSEARCH_URL="http://localhost:9200"
$env:ELASTICSEARCH_INDEX="nlp-opinion-trend-logs"
# Optional:
# $env:ELASTICSEARCH_API_KEY="YOUR_API_KEY"
# $env:ELASTICSEARCH_TIMEOUT_SECONDS="3"
```

### Text normalization

All `text` values are lowercased, URLs are removed, and whitespace is normalized.

### Notes

- Reddit does not reliably expose user city/location. Set `SIMULATE_CITY=false` to leave `city` empty.
- Set `INCLUDE_COMMENTS=false` for Reddit posts only.

## Clean the collected data

Remove rows where `text` has fewer than 4 words, remove URLs, normalize whitespace, and save to `clean_data.xlsx`:

```powershell
$env:INPUT_FILE="social_data.xlsx"
$env:CLEAN_OUTPUT_FILE="clean_data.xlsx"
$env:MIN_WORDS="4"
python clean_data.py
```

