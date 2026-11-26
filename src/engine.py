import re
from io import BytesIO
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILLS = {s: [s] for s in ['Python','Java','JavaScript','TypeScript','C++','C#','SQL','HTML','CSS','React','Node.js','Git','GitHub','Docker','Kubernetes','AWS','Azure','Linux','Pandas','NumPy','Scikit-learn','TensorFlow','PyTorch','Excel','Power BI','Tableau','Streamlit','Flask','Django','FastAPI','MongoDB','PostgreSQL','MySQL','REST API','Data Analysis','Communication','Teamwork','Problem Solving','Project Management','Figma','Agile','Testing']}
SKILLS.update({'Machine Learning':['machine learning','ML'],'Deep Learning':['deep learning'],'Natural Language Processing':['natural language processing','NLP'],'Artificial Intelligence':['artificial intelligence','AI']})

def extract_pdf(data):
    if len(data)>10*1024*1024: raise ValueError('PDF must be under 10 MB.')
    try:
        reader=PdfReader(BytesIO(data))
        if reader.is_encrypted: raise ValueError('Please upload an unlocked PDF.')
        if len(reader.pages)>50: raise ValueError('Please use a PDF with at most 50 pages.')
        text='\n'.join(p.extract_text() or '' for p in reader.pages)
    except ValueError: raise
    except Exception as e: raise ValueError('Unable to read PDF. Please upload a valid text-based PDF.') from e
    if not text.strip(): raise ValueError('No readable text found. Scanned PDFs require OCR, which is not supported.')
    return text

def skills(text):
    return {name for name, aliases in SKILLS.items() if any(re.search(r'(?<![\w+#])'+re.escape(a)+r'(?![\w+#])',text,re.I) for a in aliases)}

def analyze(resume, job):
    if not resume.strip() or not job.strip(): raise ValueError('Both documents must contain text.')
    try:
        vectors=TfidfVectorizer(stop_words='english', token_pattern=r'(?u)\b\w[\w+#.]*').fit_transform([resume,job])
    except ValueError as e: raise ValueError('Please enter meaningful text in both documents.') from e
    if not all(vectors.getnnz(axis=1)): raise ValueError('Both documents need usable terms.')
    score=float(cosine_similarity(vectors[0],vectors[1])[0,0])*100
    required=skills(job); found=skills(resume); matched=required & found; missing=required-found
    return dict(similarity=round(min(100,max(0,score)),1),coverage=round(100*len(matched)/len(required),1) if required else None,matched=sorted(matched),missing=sorted(missing),found=sorted(found),required=sorted(required))

def report(result):
    return '\n'.join(['ResumeIQ | Resume comparison report',f"Text similarity: {result['similarity']}%",f"Skill coverage: {str(result['coverage'])+'%' if result['coverage'] is not None else 'N/A'}",'Matched: '+(', '.join(result['matched']) or 'None'),'Not detected: '+(', '.join(result['missing']) or 'None'),'Suggestions: Add relevant skills only if you genuinely possess them; otherwise consider learning them.','Scores are text comparisons, not hiring probabilities or verified ATS scores.'])
