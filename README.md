# Job Application Agent — mobile review queue

A Streamlit app designed for Chrome on Android and desktop. This version is a review tracker and preference dashboard, not yet a live job-search bot. It does not scrape job boards, log in to job sites, fill application forms, or submit applications.

## Current search specification

- Minimum acceptable compensation: **₹10 LPA**.
- Preferred compensation range: **₹10–20 LPA**.
- Target roles: **Dynamics 365 CRM Developer, D365 Technical Consultant, Senior D365 CE Consultant, Power Platform Developer**.
- Location: **India — remote, hybrid, or onsite**, with explicit verification that remote jobs accept applicants based in India.
- Resume source: the user's uploaded `5Power Platform_YATISH MAHAJAN_CRM.pdf`. The app does not yet parse the PDF automatically; verify all employment dates and application answers before use.
- Daily review target: **10 jobs**. The dashboard shows a count of distinct jobs whose status changed today (UTC); it is a progress indicator, not a promise that ten matching jobs will exist each day.
- Salary handling: jobs with an undisclosed salary should be marked for recruiter verification. Do not assume unknown compensation is at least ₹10 LPA.
- Submission safety: **mandatory human approval before any application submission**. In this version, approval only changes the queue status and never submits anything.

## Current features

- Add a job manually with URL, title, company, location, salary, match score, and explanation.
- Approve, reject, save for later, or return to pending review.
- Search/filter jobs, see status counts, save review notes, and export CSV.
- Duplicate URL prevention and status-change history.
- Responsive layout and larger mobile tap targets.
- Optional password gate controlled by Streamlit secret `APP_PASSWORD`.
- Visible target roles, salary preferences, location, resume source, and daily review progress.

## Deploy free to Streamlit Community Cloud

1. Create a private GitHub repository named `job-application-agent`.
2. Upload `app.py`, `requirements.txt`, and `README.md` to the repository root. Do not upload your resume, `jobs.db`, passwords, or other personal data.
3. Open https://share.streamlit.io/ and sign in with GitHub.
4. Select **Create app**, choose the repository and branch, and set the main file path to `app.py`.
5. In **App settings → Secrets**, add a strong unique password:

   ```toml
   APP_PASSWORD = "replace-with-a-long-unique-password"
   ```

6. Save and wait for the app to restart. Open its `*.streamlit.app` URL in Chrome on Android. Bookmark it or choose Chrome's **Add to Home screen**.
7. Test the password gate and review actions before entering real job data.

Official deployment instructions: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## Important persistence warning

Records are currently stored in `jobs.db` beside `app.py`. Streamlit Community Cloud does not guarantee persistence of local files; restarts/redeployments may lose the database. Treat cloud deployment as a demo until persistent storage is added (for example, Supabase/Postgres). Configure database credentials in Streamlit Secrets. Do not commit secrets or personal data to GitHub.

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

## Not implemented yet

- Live job discovery or official integrations for LinkedIn, Naukri, Foundit, FlexJobs, Arc.dev, remote boards, or company career sites.
- Automatic PDF resume parsing and evidence-based match scoring.
- Automatic salary/location verification.
- Persistent cloud database.
- Application form filling or submission.

Implement these in separate, tested phases, following each site's terms and preserving human approval before submission.
