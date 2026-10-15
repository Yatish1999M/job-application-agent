# Job Application Agent — mobile-friendly review queue

A Streamlit app designed to work in Chrome on Android and desktop. It is a review tracker, not an autonomous application bot. It does not scrape job boards, log in to job sites, or submit applications.

## Current features

- Add a job manually with URL, title, company, location, salary, match score, and explanation.
- Approve, reject, save for later, or return to pending review.
- Search/filter jobs, see state counts, save review notes, and export CSV.
- Duplicate URL prevention and status-change history.
- Responsive layout and larger mobile tap targets.
- Optional password gate controlled by Streamlit secret `APP_PASSWORD`.
- Approval only changes the review state. It never submits an application.

## Deploy free to Streamlit Community Cloud

1. Create a GitHub account if you do not already have one.
2. Create a **private GitHub repository** named `job-application-agent` (recommended for source control; the app itself still needs its own access protection).
3. Upload `app.py` and `requirements.txt` to the repository root. Do not upload your resume, `jobs.db`, passwords, or other personal data.
4. Open https://share.streamlit.io/ and sign in with GitHub.
5. Select **Create app**, choose the repository and branch, and set the main file path to `app.py`.
6. Before sharing/opening the deployed app, open **App settings → Secrets** and add this TOML entry, replacing the example with a strong unique password:

   ```toml
   APP_PASSWORD = "replace-with-a-long-unique-password"
   ```

7. Save secrets, allow the app to redeploy, then open its `*.streamlit.app` URL in Chrome on Android. Bookmark it or use Chrome's **Add to Home screen** option.
8. Test the password gate and review actions before entering any real job data.

Official deployment instructions: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## Important persistence warning

The current version stores records in `jobs.db` beside `app.py`. Streamlit Community Cloud explicitly does not guarantee persistence of local files; app restarts/redeployments may lose the database. Therefore, this cloud deployment is suitable for a demo/test only until persistent storage is added. For reliable long-term use, connect a persistent database (for example, Supabase/Postgres) and configure its credentials using Streamlit Secrets. Do not assume CSV export is a backup unless you download and keep it somewhere safe.

## Local setup

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Security

- Do not commit `.streamlit/secrets.toml`, passwords, resume files, or `jobs.db` to GitHub.
- Password gate is a basic single-user barrier, not enterprise authentication. Use a long unique password and keep the repository private.
- A cloud-hosted app runs on a third-party service; consider privacy before entering sensitive notes or personal information.
- Do not store website passwords or OTPs in the agent.

## Not implemented yet

- Automatic job discovery or live integrations with LinkedIn, Naukri, Foundit, or remote-job boards.
- Automatic PDF resume parsing or AI match scoring.
- Persistent cloud database.
- Automated form filling or application submission.

These should be added in separate, tested phases while preserving human approval before submission.
