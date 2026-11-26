# ResumeIQ Pro V2
Explainable career assistant built with Streamlit, TF-IDF and cosine similarity.

## Run on Windows
Open this folder in VS Code. In PowerShell run:
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```
Select Try sample demo and Analyze resume. Download the PDF report, edit the draft and download the resume. For your own resume, upload a text-based PDF or paste text. Paste job requirements or retrieve a public job URL and review the extracted text. If extraction fails, paste manually. The application link opens the job page; submit manually.

## Methodology
TF-IDF fits a shared vocabulary on the two inputs; cosine similarity compares their vectors. A curated skill dictionary detects terms and aliases. Coverage is matched skills divided by detected required skills. Draft generation reorders existing bullet groups by relevance; it does not invent qualifications. No supervised model training or external AI API. PDF exports use ReportLab. Public HTML extraction uses BeautifulSoup and validates public IPs, including redirects. No OCR or JavaScript rendering. Scores are not ATS scores or hiring probabilities. PDF export supports Latin text; unsupported characters may be replaced. Avoid uploading sensitive information to public deployments. Inputs are held in session memory, not intentionally saved to disk.

## Test
`python -m unittest discover -s tests -v`
14 core tests passed in the build environment. Streamlit UI and live external URL fetching were not tested there. Test both locally before deployment.

## Deploy
Publish this folder as a new public GitHub repository (do not include .venv or personal resumes). On Streamlit Community Cloud select the repository, branch and app.py. Use Python 3.12 if available. MIT license included.
