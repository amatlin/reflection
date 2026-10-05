# Cloud Run Migration Runbook

Moving the Reflection web app from Railway to Google Cloud Run. Context: the Railway trial expired 2026-04-15 and the site went down (see `LAB_NOTEBOOK.md`, 2026-10-05).

**Why Cloud Run:** same Google Cloud project and bill as BigQuery, scale-to-zero pricing (~$0–2/month at current traffic vs. ~$5/month flat on Railway), and no trial to expire.

**What doesn't change:** the code, the Dockerfile, Supabase, PostHog, dbt, Stripe (same domain), DNS registrar (Namecheap).

## Values used throughout

| Thing | Value | Where it comes from |
|---|---|---|
| GCP project | `reflection-data` | `pipeline/dbt/profiles.yml` |
| Region | `us-central1` | BigQuery dataset is in the `US` multi-region; `us-central1` is close to it and supports Cloud Run domain mappings |
| Service name | `reflection` | new |
| Runtime service account | `reflection-web@reflection-data.iam.gserviceaccount.com` | new |
| Domain | `www.reflection.sh` (apex `reflection.sh` redirects to www at Namecheap) | existing |

Run everything below **on your laptop** from the repo root, in a terminal. Set these once per terminal session:

```bash
export PROJECT=reflection-data
export REGION=us-central1
export SA=reflection-web@${PROJECT}.iam.gserviceaccount.com
```

---

## Step 0 — Install and log in to gcloud

`gcloud` is Google Cloud's command-line tool (like the `railway` CLI, but for GCP).

```bash
brew install --cask google-cloud-sdk   # skip if `gcloud --version` already works
gcloud auth login                      # opens a browser to sign in
gcloud config set project $PROJECT     # make reflection-data the default project
```

## Step 1 — Check billing is on

Cloud Run (and BigQuery, and the PostHog export into it) need an active billing account on the project. If the project was on the $300 free trial, the trial has ended and billing may have been switched off.

```bash
gcloud billing projects describe $PROJECT
```

- `billingEnabled: true` → good, continue.
- `billingEnabled: false` → list your billing accounts and link one:
  ```bash
  gcloud billing accounts list
  gcloud billing projects link $PROJECT --billing-account=XXXXXX-XXXXXX-XXXXXX
  ```
  If the only billing account is a closed free trial, open https://console.cloud.google.com/billing and click **Upgrade** / **Activate** to convert it to a paid account first.

Save the billing account ID for the next step:

```bash
export BILLING=$(gcloud billing projects describe $PROJECT --format='value(billingAccountName)' | sed 's|billingAccounts/||')
echo $BILLING
```

## Step 2 — Budget alert ($5/month)

A budget **emails you** at 50%, 90% and 100% of $5. It does **not** stop spending — it's an alarm, not a circuit breaker.

```bash
gcloud services enable billingbudgets.googleapis.com
gcloud billing budgets create \
  --billing-account=$BILLING \
  --display-name="reflection monthly" \
  --budget-amount=5USD \
  --threshold-rule=percent=0.5 \
  --threshold-rule=percent=0.9 \
  --threshold-rule=percent=1.0
```

Alerts go to the billing account's admins (your Google account) by default.

## Step 3 — Turn on the Google Cloud services we need

Each Google Cloud product is an "API" that has to be switched on per project:

- **Cloud Run** runs the container.
- **Cloud Build** builds the container from the Dockerfile.
- **Artifact Registry** stores built containers.
- **Secret Manager** holds API keys.

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

## Step 4 — Create the app's service account

A service account is a robot identity. On Railway, the app logged into BigQuery with a pasted JSON key (`BIGQUERY_KEY_JSON`). On Cloud Run, the app *runs as* this service account, and `bigquery_client.py` already falls back to that automatic login when no key is set. No key to leak or rotate.

The app only reads from BigQuery, so it gets read-only access plus permission to run queries:

```bash
gcloud iam service-accounts create reflection-web \
  --display-name="Reflection web app (Cloud Run)"

# Read tables
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA" --role="roles/bigquery.dataViewer"

# Run query jobs
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA" --role="roles/bigquery.jobUser"

# Read secrets (Step 5)
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA" --role="roles/secretmanager.secretAccessor"
```

## Step 5 — Store secret keys in Secret Manager

Secret keys go into Secret Manager rather than plain environment variables, so they aren't visible in the Cloud Run console or deploy history. This loop reads each value from your local `.env`, so the keys never get typed into your shell history:

```bash
for KEY in SUPABASE_ANON_KEY SUPABASE_SERVICE_ROLE_KEY ANTHROPIC_API_KEY \
           STRIPE_SECRET_KEY STRIPE_WEBHOOK_SECRET OPENAI_API_KEY; do
  VALUE=$(grep "^${KEY}=" .env | cut -d= -f2-)
  if [ -n "$VALUE" ]; then
    printf '%s' "$VALUE" | gcloud secrets create "$KEY" --data-file=- \
      && echo "created $KEY"
  else
    echo "skipped $KEY (not in .env)"
  fi
done
```

Notes:
- If a value in `.env` is wrapped in quotes, remove the quotes first (or the quotes get stored too).
- **If Supabase had to be recreated** (see Step 10), use the *new* project's keys.
- To change a secret later: `printf '%s' "NEW_VALUE" | gcloud secrets versions add KEY --data-file=-`, then redeploy.

## Step 6 — Deploy

`--source .` uploads the repo, Cloud Build builds it with our `Dockerfile`, and Cloud Run starts it. `.gcloudignore` keeps `.env`, keys, and `.git` out of the upload.

Fill in the three public values from your `.env` (these are safe as plain env vars: PostHog's `phc_` key and Stripe's `pk_` key are designed to be public, and the Supabase URL isn't secret). Then drop any `--set-secrets` entry that Step 5 skipped:

```bash
gcloud run deploy reflection \
  --source . \
  --region $REGION \
  --service-account $SA \
  --allow-unauthenticated \
  --max-instances 1 \
  --concurrency 250 \
  --timeout 3600 \
  --cpu 1 --memory 512Mi \
  --set-env-vars "BIGQUERY_PROJECT=$PROJECT,BIGQUERY_DATASET=reflection,POSTHOG_HOST=https://us.i.posthog.com,POSTHOG_API_KEY=phc_...,SUPABASE_URL=https://xxxx.supabase.co,STRIPE_PUBLISHABLE_KEY=pk_..." \
  --set-secrets "SUPABASE_ANON_KEY=SUPABASE_ANON_KEY:latest,SUPABASE_SERVICE_ROLE_KEY=SUPABASE_SERVICE_ROLE_KEY:latest,ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest,STRIPE_SECRET_KEY=STRIPE_SECRET_KEY:latest,STRIPE_WEBHOOK_SECRET=STRIPE_WEBHOOK_SECRET:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest"
```

If it asks to create an Artifact Registry repository, answer **Y**. The first build takes a few minutes.

What each flag is for:

| Flag | Why |
|---|---|
| `--allow-unauthenticated` | It's a public website: anyone can load it without a Google login. |
| `--max-instances 1` | **Required.** The live stream broadcasts in-process (`events.py` keeps the set of open WebSockets in memory). Two instances would split visitors into two rooms that can't see each other's events. |
| `--concurrency 250` | Each open WebSocket counts as an in-flight request. The default (80) would turn away the 81st simultaneous visitor with only one instance allowed. |
| `--timeout 3600` | Longest a request may stay open: 60 minutes, the maximum. WebSockets get cut after this; `stream.js` reconnects automatically. |
| `--cpu 1 --memory 512Mi` | Small and cheap. If logs show out-of-memory crashes, raise to `1Gi`. |
| (no `--min-instances`) | Scale to zero when idle → ~$0. The trade-off is a few seconds of cold start for the first visitor after a quiet period. |
| `BIGQUERY_KEY_JSON` not set | On purpose: the app falls back to running as the service account. |

## Step 7 — Smoke test on the temporary URL

The deploy prints a URL like `https://reflection-xxxxxxxx-uc.a.run.app`.

```bash
URL=$(gcloud run services describe reflection --region $REGION --format='value(status.url)')
curl -s -o /dev/null -w "%{http_code}\n" $URL                       # expect 200
curl -s $URL/api/warehouse/events-by-type | head -c 300; echo         # expect JSON with rows
gcloud run services logs read reflection --region $REGION --limit 50  # look for errors
```

Then open `$URL` in a browser:
- Homepage loads with your visitor ID
- **Streaming** strip fills with events (→ Supabase works)
- A **warehouse** chip returns rows (→ BigQuery + service account work)
- An **insight** chip shows a Claude summary (→ Anthropic key works)
- Enter the exhibit, click through all 5 steps, try it at phone width

Stripe checkout won't fully complete here: Stripe sends its webhook to `www.reflection.sh`, which still points at Railway until Step 9.

## Step 8 — Auto-delete old container builds

Every deploy stores a new container image (~100–200 MB). Keep the latest 3 and delete the rest so storage stays inside the free 0.5 GB:

```bash
cat > /tmp/cleanup-policy.json <<'EOF'
[
  {"name": "keep-latest-3", "action": {"type": "Keep"}, "mostRecentVersions": {"keepCount": 3}},
  {"name": "delete-older", "action": {"type": "Delete"}, "condition": {"olderThan": "7d"}}
]
EOF
gcloud artifacts repositories set-cleanup-policies cloud-run-source-deploy \
  --location=$REGION --policy=/tmp/cleanup-policy.json --no-dry-run
```

## Step 9 — Point www.reflection.sh at Cloud Run

Cloud Run domain mapping is free but still marked **preview** by Google. If it misbehaves, the fallback is Firebase Hosting in front of the Cloud Run service (also free).

**9a. Prove you own the domain** (one time). This opens Google Search Console and gives you a TXT record to add at Namecheap (Domain List → Manage → Advanced DNS → Add New Record → TXT, host `@`):

```bash
gcloud domains verify reflection.sh
gcloud domains list-user-verified        # re-run until reflection.sh appears
```

**9b. Create the mapping:**

```bash
gcloud beta run domain-mappings create \
  --service reflection --domain www.reflection.sh --region $REGION
gcloud beta run domain-mappings describe \
  --domain www.reflection.sh --region $REGION   # shows the DNS record to set
```

**9c. Update DNS at Namecheap:**
- Change the `www` CNAME from `hi6tzv2n.up.railway.app` → `ghs.googlehosted.com.`
- Delete the old `_railway-verify.www` TXT record
- Leave the apex `reflection.sh` → `www` redirect as it is

DNS changes take minutes to an hour to spread. After that, Google issues the HTTPS certificate automatically, which can take up to roughly an hour. Until then, browsers show a certificate warning for www.reflection.sh. Check progress with the `describe` command above; the conditions turn `True` once it's ready.

**9d. Final checks on https://www.reflection.sh:** repeat the Step 7 browser checklist, then do one Stripe test donation (sandbox mode) and confirm the `purchase_complete` event shows up in the stream.

## Step 10 — Everything outside Cloud Run

Hosting is only one of the services that stopped. Bring back the rest:

1. **Supabase:** if the project is paused, click **Restore** in the dashboard. If it can't be restored, create a new project, recreate the `events` table, then update the `SUPABASE_URL` env var and the two Supabase secrets, and redeploy.
2. **PostHog → BigQuery export:** in PostHog, Data pipelines → the BigQuery destination. Check its run history. If it was paused after repeated failures, re-enable it once billing (Step 1) is confirmed.
3. **dbt daily build:** GitHub → Actions → "dbt build" → **Enable workflow**, then **Run workflow** once to test. GitHub turned it off on 2026-05-30 after 60 days with no commits. It still uses the `BIGQUERY_KEY_JSON` GitHub secret, which is unaffected by this migration.
4. **Railway:** once www.reflection.sh has served from Cloud Run for a few days, delete the Railway project.
5. **Docs:** update `README.md` (Deployment, Stack) and `architecture.md` (Hosting, BIGQUERY_KEY_JSON notes) to say Cloud Run. Add a lab notebook entry.

## Redeploying later

Same command as Step 6. Env vars and secrets persist on the service, so after the first deploy this is enough:

```bash
gcloud run deploy reflection --source . --region us-central1
```

## Rollback

Cloud Run keeps previous revisions. To go back to the last working version:

```bash
gcloud run revisions list --service reflection --region us-central1
gcloud run services update-traffic reflection --region us-central1 --to-revisions REVISION_NAME=100
```
