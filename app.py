from pathlib import Path
from urllib.parse import urlsplit
import streamlit as st
from src.engine import analyze, extract_pdf, report
from src.pro import fetch_job, suggestions, draft_resume, pdf_bytes
ROOT=Path(__file__).parent
st.set_page_config(page_title='ResumeIQ Pro | Career Intelligence',page_icon='🎯',layout='wide')
st.markdown((ROOT/'assets/style.html').read_text(encoding='utf-8'),unsafe_allow_html=True)
st.sidebar.title('🎯 ResumeIQ Pro');st.sidebar.caption('CAREER INTELLIGENCE / V2.0')
page=st.sidebar.radio('Navigation',['Resume analyzer','How it works'])
st.sidebar.info('NLP • TF-IDF • Cosine similarity')
if page=='How it works':
    st.title('How ResumeIQ Pro works')
    st.markdown('''1. Extract text from a PDF or accept pasted text.\n2. Retrieve public job page text when available, or accept manual input.\n3. Fit TF-IDF on the two documents and calculate cosine similarity.\n4. Compare supported skill keywords and suggest improvements.\n5. Reorder relevant existing bullets, allow editing and export PDFs.\n6. Open the job page for manual application.\n\nNo supervised training, paid AI API, OCR or automatic application submission. Scores are not hiring probabilities or validated ATS scores. Keyword matching cannot verify expertise. Public job pages may block extraction; always review retrieved text. PDF export supports Latin text; unsupported characters may be replaced. Uploaded text is held in session memory, not intentionally saved to disk.''')
    st.latex(r'\cos(\theta)=\frac{A\cdot B}{\|A\|\|B\|}');st.stop()
st.markdown("""
<style>
.resumeiq-hero {
    text-align: center;
    padding: 38px 20px 30px;
    margin-bottom: 25px;
    border: 1px solid #303b55;
    border-radius: 24px;
    background: radial-gradient(
        ellipse at top, #252044 0%, #111827 65%
    );
    animation: heroFade 0.8s ease-out;
}
.resumeiq-label {
    color: #a78bfa;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 3px;
}
.resumeiq-brand {
    font-size: clamp(38px, 6vw, 72px);
    font-weight: 900;
    letter-spacing: -2px;
    margin: 12px 0;
    background: linear-gradient(
        90deg, #818cf8, #c084fc, #60a5fa
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.resumeiq-tagline {
    color: #f8fafc;
    font-size: 25px;
    font-weight: 600;
}
.resumeiq-description {
    color: #94a3b8;
    font-size: 15px;
    margin: 12px 0 24px;
}
.resumeiq-features {
    display: flex;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
}
.resumeiq-feature {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 14px 20px;
    color: #c4b5fd;
    font-size: 14px;
    font-weight: 600;
    transition: 0.3s;
}
.resumeiq-feature:hover {
    transform: translateY(-4px);
    border-color: #a78bfa;
    box-shadow: 0 0 20px #8b5cf640;
}
@keyframes heroFade {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>

<div class="resumeiq-hero">
    <div class="resumeiq-label">
        ✦ INTELLIGENT CAREER PLATFORM
    </div>
    <div class="resumeiq-brand">ResumeIQ Pro</div>
    <div class="resumeiq-tagline">
        Your Career. Intelligently Optimized.
    </div>
    <div class="resumeiq-description">
        Analyze smarter. Discover skill gaps.
        Build better resumes.
    </div>
    <div class="resumeiq-features">
        <div class="resumeiq-feature">🧠 NLP Powered</div>
        <div class="resumeiq-feature">🎯 Smart Job Matching</div>
        <div class="resumeiq-feature">📊 Resume Intelligence</div>
    </div>
</div>
""", unsafe_allow_html=True)

mode=st.radio('Workspace',['Try sample demo','Analyze my resume'],horizontal=True)
a,b=st.columns(2)
with a:
    st.subheader('01 · Resume')
    if mode=='Try sample demo':resume=st.text_area('Sample resume',(ROOT/'samples/resume.txt').read_text(),height=240,key='sample_resume')
    else:
        rm=st.radio('Resume input',['Upload PDF','Paste text'],horizontal=True)
        resume=''
        if rm=='Upload PDF':
            f=st.file_uploader('Text-based PDF (max 10 MB)',type=['pdf'])
            if f:
                try:resume=extract_pdf(f.getvalue());st.success('Resume text extracted.')
                except ValueError as e:st.error(str(e))
        else:resume=st.text_area('Paste resume text',height=240,max_chars=30000)
        st.caption('Redact sensitive personal information before uploading.')
with b:
    st.subheader('02 · Job requirements')
    url=''
    if mode=='Try sample demo':job=st.text_area('Sample job description',(ROOT/'samples/job.txt').read_text(),height=240,key='sample_job')
    else:
        jm=st.radio('Job input',['Paste description','Job URL'],horizontal=True)
        if jm=='Job URL':
            url=st.text_input('Public job posting URL')
            if st.button('Extract job description'):
                st.session_state['url_job']=''
                try:
                    with st.spinner('Reading public job page…'):st.session_state['url_job']=fetch_job(url)
                    st.success('Text retrieved. Review and remove unrelated content.')
                except Exception:st.warning('Could not retrieve this page. Paste the job description below instead.')
            job=st.text_area('Review or paste job description',height=240,key='url_job',max_chars=30000)
        else:
            job=st.text_area('Paste job description',height=240,max_chars=30000)
            url=st.text_input('Application URL (optional)')
if st.button('Analyze resume',type='primary',use_container_width=True):
    st.session_state.pop('analysis',None)
    try:
        r=analyze(resume,job);st.session_state['analysis']=(mode,resume,job,url,r);st.session_state['draft']=draft_resume(resume,r)
    except ValueError as e:st.error(str(e))
if 'analysis' in st.session_state and st.session_state['analysis'][0]==mode:
    _,original,requirements,application,r=st.session_state['analysis']
    st.divider();st.subheader('03 · Match intelligence');st.caption('Results from last analysis. Re-analyze after changing inputs.')
    a,b,c=st.columns(3);a.metric('Text similarity',f"{r['similarity']}%");b.metric('Skill coverage',f"{r['coverage']}%" if r['coverage'] is not None else 'N/A');c.metric('Skills not detected',len(r['missing']))
    st.progress(r['similarity']/100,text='TF-IDF cosine similarity')
    if r['coverage'] is not None:st.progress(r['coverage']/100,text='Detected skill coverage')
    a,b=st.columns(2);a.success('Matched: '+(', '.join(r['matched']) or 'None'));b.warning('Not detected: '+(', '.join(r['missing']) or 'None'))
    if r['required']:
        import altair as alt
        import pandas as pd

        matched = len(r['matched'])
        total = len(r['required'])
        missing = total - matched

        chart_data = pd.DataFrame({
            'Status': ['Matched skills', 'Undetected skills'],
            'Count': [matched, missing]
        })

        donut = alt.Chart(chart_data).mark_arc(
            innerRadius=75, outerRadius=110
        ).encode(
            theta=alt.Theta('Count:Q'),
            color=alt.Color(
                'Status:N',
                scale=alt.Scale(
                    domain=['Matched skills', 'Undetected skills'],
                    range=['#16A34A', '#EAB308']
                ),
                legend=alt.Legend(title='Skill Distribution')
            ),
            tooltip=['Status:N', 'Count:Q']
        )

        center = alt.Chart(pd.DataFrame({
            'label': [f'{matched}/{total}']
        })).mark_text(
            fontSize=32, fontWeight='bold', color='white'
        ).encode(text='label:N')

        st.altair_chart(
            (donut + center).properties(height=280),
            use_container_width=True
        )
    tips=suggestions(r,original);st.subheader('04 · Improvement roadmap')
    for tip in tips:st.write('• '+tip)
    st.download_button('Download analysis report (PDF)',pdf_bytes('ResumeIQ | Analysis report',report(r)+'\n\nImprovement roadmap\n'+'\n'.join(tips)),'ResumeIQ_report.pdf','application/pdf')
    st.subheader('05 · Editable resume studio');st.caption('Draft preserves original text and prioritizes relevant bullets within existing groups. Review and edit; never add false claims.')
    edited=st.text_area('Your editable resume',key='draft',height=300)
    if edited.strip():
        st.download_button('Download edited resume (PDF)',pdf_bytes('Resume',edited),'ResumeIQ_resume.pdf','application/pdf')
        if st.button('Compare edited resume'):
            try:
                updated=analyze(edited,requirements);st.write(f"Updated text similarity: {updated['similarity']}% | Skill coverage: {updated['coverage'] if updated['coverage'] is not None else 'N/A'}" )
            except ValueError as e:st.error(str(e))
    st.subheader('06 · Apply for the job')
    try:
        p=urlsplit(application);valid=p.scheme in ('https','http') and p.hostname and not p.username and not p.password
    except ValueError:valid=False
    if valid:st.link_button('Open job application page ↗',application);st.caption('Verify the destination and submit your downloaded resume manually.')
    else:st.info('Enter a job URL in your own resume workspace and analyze to enable the application link.')
    st.caption('Scores are text comparisons, not verified ATS scores or hiring probabilities.')
st.divider();st.caption('ResumeIQ Pro • Explainable NLP • No paid API required')
