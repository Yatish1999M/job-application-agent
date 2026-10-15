import sqlite3
import hmac
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st

DB = Path(__file__).with_name('jobs.db')
STATES = ('Pending Review', 'Approved', 'Rejected', 'Saved for Later')

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, company TEXT NOT NULL, url TEXT NOT NULL UNIQUE,
        location TEXT DEFAULT '', salary TEXT DEFAULT '', match_score INTEGER DEFAULT 0,
        match_reason TEXT DEFAULT '', notes TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'Pending Review',
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL
    )''')
    con.execute('''CREATE TABLE IF NOT EXISTS status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER NOT NULL,
        previous_status TEXT NOT NULL, new_status TEXT NOT NULL,
        changed_at TEXT NOT NULL, FOREIGN KEY(job_id) REFERENCES jobs(id)
    )''')
    con.commit()
    return con

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def add_job(title, company, url, location, salary, score, reason):
    with connect() as con:
        con.execute('''INSERT INTO jobs(title,company,url,location,salary,match_score,match_reason,created_at,updated_at)
                       VALUES(?,?,?,?,?,?,?,?,?)''',
                    (title.strip(),company.strip(),url.strip(),location.strip(),salary.strip(),score,reason.strip(),now(),now()))

def set_status(job_id, new_status, notes):
    if new_status not in STATES: raise ValueError('Invalid status')
    with connect() as con:
        old = con.execute('SELECT status FROM jobs WHERE id=?',(job_id,)).fetchone()
        if old is None: raise ValueError('Job not found')
        con.execute('UPDATE jobs SET status=?,notes=?,updated_at=? WHERE id=?',
                    (new_status,notes,now(),job_id))
        if old['status'] != new_status:
            con.execute('INSERT INTO status_history(job_id,previous_status,new_status,changed_at) VALUES(?,?,?,?)',
                        (job_id,old['status'],new_status,now()))

st.set_page_config(page_title='Job Application Agent', page_icon='📋', layout='wide', initial_sidebar_state='collapsed')

# Mobile-friendly layout and larger tap targets.
st.markdown('''
<style>
  .block-container {padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1100px;}
  div.stButton > button, div.stFormSubmitButton > button, div.stDownloadButton > button {min-height: 2.8rem; width: 100%; white-space: normal;}
  a[data-testid="stLinkButton"] {min-height: 2.7rem;}
  @media (max-width: 640px) {
    .block-container {padding-left: 0.8rem; padding-right: 0.8rem;}
    h1 {font-size: 1.55rem !important; line-height: 1.25 !important;}
    h2 {font-size: 1.25rem !important;}
    h3 {font-size: 1.05rem !important;}
    [data-testid="stMetric"] {padding: 0.55rem 0.35rem;}
    [data-testid="stMetricValue"] {font-size: 1.2rem !important;}
    div[data-testid="stHorizontalBlock"] {gap: 0.45rem;}
  }
</style>
''', unsafe_allow_html=True)

# Optional password gate: configure APP_PASSWORD in Streamlit secrets before cloud deployment.
# If no password is configured, show a prominent warning rather than pretending the app is private.
try:
    app_password = st.secrets.get('APP_PASSWORD', '')
except Exception:
    app_password = ''
if app_password:
    if not st.session_state.get('authenticated', False):
        st.title('🔐 Job Application Agent')
        st.caption('Private access')
        with st.form('login_form'):
            entered = st.text_input('App password', type='password')
            login = st.form_submit_button('Unlock agent', use_container_width=True)
        if login:
            if hmac.compare_digest(entered, app_password):
                st.session_state['authenticated'] = True
                st.rerun()
            st.error('Incorrect password.')
        st.stop()
else:
    st.warning('Security setup required before deployment: add APP_PASSWORD in Streamlit Cloud → App settings → Secrets. Do not use this app with personal data until access is protected.')

st.title('📋 Job Application Agent')
st.caption('Mobile-friendly review queue · Approval NEVER submits an application.')

with st.sidebar:
    st.header('Add a job')
    st.caption('Add a listing to review. Matching scores are entered manually in this version.')
    with st.form('add_job',clear_on_submit=True):
        title=st.text_input('Job title')
        company=st.text_input('Company')
        url=st.text_input('Job URL (https://...)')
        location=st.text_input('Location',value='India')
        salary=st.text_input('Salary (if disclosed)')
        score=st.slider('Match score',0,100,70)
        reason=st.text_area('Why this job matches')
        submitted=st.form_submit_button('Add to review queue',use_container_width=True)
        if submitted:
            if not title.strip() or not company.strip() or not url.startswith('https://'):
                st.error('Enter a title, company and valid https:// job URL.')
            else:
                try:
                    add_job(title,company,url,location,salary,score,reason)
                    st.success('Job added.')
                except sqlite3.IntegrityError:
                    st.warning('This job URL is already in your queue.')

with connect() as con:
    rows=[dict(x) for x in con.execute('SELECT * FROM jobs ORDER BY match_score DESC, created_at DESC').fetchall()]

cols=st.columns(4)
for col,status in zip(cols,STATES):
    col.metric(status,sum(r['status']==status for r in rows))

status_filter=st.selectbox('Filter status',['All',*STATES])
search=st.text_input('Search title or company')
filtered=[r for r in rows if (status_filter=='All' or r['status']==status_filter)
          and search.lower() in (r['title']+' '+r['company']).lower()]

if not filtered:
    st.info('No jobs match the current filter. Add a job using the sidebar.')

for job in filtered:
    with st.container(border=True):
        left,right=st.columns([4,1])
        with left:
            st.subheader(f"{job['title']} — {job['company']}")
            st.write(f"📍 {job['location'] or 'Not specified'}  ·  💰 {job['salary'] or 'Not disclosed'}  ·  Match: **{job['match_score']}/100**")
            st.write(job['match_reason'] or 'No match explanation provided.')
            st.link_button('View original job',job['url'])
        with right:
            st.markdown(f"**Status:** {job['status']}")
        with st.form(f"review_{job['id']}"):
            notes=st.text_area('Review notes',value=job['notes'],key=f"notes_{job['id']}")
            a,b,c,d=st.columns(4)
            approve=a.form_submit_button('✓ Approve',use_container_width=True)
            reject=b.form_submit_button('✕ Reject',use_container_width=True)
            later=c.form_submit_button('☆ Save for later',use_container_width=True)
            pending=d.form_submit_button('↺ Return to pending',use_container_width=True)
            if approve or reject or later or pending:
                status=('Approved' if approve else 'Rejected' if reject else 'Saved for Later' if later else 'Pending Review')
                set_status(job['id'],status,notes)
                st.rerun()

if rows:
    import csv,io
    buf=io.StringIO()
    writer=csv.DictWriter(buf,fieldnames=list(rows[0].keys()))
    writer.writeheader();writer.writerows(rows)
    st.download_button('Export queue as CSV',buf.getvalue(),'job_review_queue.csv','text/csv')

st.divider()
st.info('Approved means reviewed and approved for manual application only. This app has no application submission, website scraping, browser automation, or external API calls.')
st.caption('Cloud note: Streamlit Community Cloud does not guarantee local SQLite file persistence. Use an external persistent database before relying on this as your only tracker.')
