import re, json, socket, ipaddress, http.client, ssl
from urllib.parse import urlsplit, urljoin
from io import BytesIO
from html import escape
from bs4 import BeautifulSoup
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from .engine import skills

def public_url(url):
    p=urlsplit(url.strip())
    if p.scheme not in ('http','https') or not p.hostname or p.username or p.password or p.port not in (None,80 if p.scheme=='http' else 443):
        raise ValueError('Enter a public HTTP or HTTPS job URL.')
    addresses=socket.getaddrinfo(p.hostname,p.port or (443 if p.scheme=='https' else 80),type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError('Private or local network addresses are not allowed.')
    return p, addresses[0][4][0]

def parse_job(html):
    soup=BeautifulSoup(html,'html.parser')
    def walk(obj):
        if isinstance(obj,dict):
            t=obj.get('@type',[])
            if 'JobPosting' in ([t] if isinstance(t,str) else t) and obj.get('description'):
                return BeautifulSoup(str(obj['description']),'html.parser').get_text(' ',strip=True)
            for v in obj.values():
                r=walk(v)
                if r:return r
        elif isinstance(obj,list):
            for v in obj:
                r=walk(v)
                if r:return r
    for tag in soup.find_all('script',type='application/ld+json'):
        try:
            r=walk(json.loads(tag.get_text()));
            if r and len(r)>80:return r
        except (ValueError,TypeError):pass
    for tag in soup(['script','style','nav','footer','header','aside','form']):tag.decompose()
    main=soup.find('main') or soup.find('article') or soup.body or soup
    text=main.get_text('\n',strip=True)
    if len(text)<150 or re.search(r'captcha|verify you are human|access denied|enable javascript',text[:500],re.I):raise ValueError('No readable job description found. Paste it manually.')
    return text[:30000]

def fetch_job(url):
    # Connect to the validated IP, preserving the hostname for TLS and Host header.
    for _ in range(4):
        p,ip=public_url(url)
        port=p.port or (443 if p.scheme=='https' else 80)
        conn=http.client.HTTPSConnection(p.hostname,port,timeout=8,context=ssl.create_default_context()) if p.scheme=='https' else http.client.HTTPConnection(p.hostname,port,timeout=8)
        conn._create_connection=lambda address,timeout,source_address=None: socket.create_connection((ip,port),timeout,source_address)
        try:
            conn.request('GET',(p.path or '/')+('?' + p.query if p.query else ''),headers={'User-Agent':'ResumeIQ/2.0','Accept':'text/html','Accept-Encoding':'identity'})
            res=conn.getresponse()
            if res.status in (301,302,303,307,308):
                url=urljoin(url,res.getheader('Location',''));continue
            if res.status!=200 or 'html' not in res.getheader('Content-Type','').lower():raise ValueError('Job page unavailable. Paste the description manually.')
            data=res.read(2000001)
            if len(data)>2000000:raise ValueError('Page too large. Paste the description manually.')
            return parse_job(data)
        finally:conn.close()
    raise ValueError('Too many redirects. Paste the description manually.')

def suggestions(r,resume):
    out=['Tailor your summary to the role using only verified experience.','Use clear headings and concise bullets; quantify achievements only with real figures.']
    if r['matched']:out.append('Highlight evidence of these detected skills: '+', '.join(r['matched'])+'.')
    if r['missing']:out.append('Review these undetected requirements: '+', '.join(r['missing'])+'. Add only if genuinely possessed; otherwise consider learning them.')
    if not re.search(r'\b(projects?|experience)\b',resume,re.I):out.append('Consider adding a clearly labelled projects or experience section if applicable.')
    if not re.search(r'\beducation\b',resume,re.I):out.append('Consider a clearly labelled education section if applicable.')
    return out

def draft_resume(resume,r):
    # Preserve original content; reorder bullets within contiguous bullet groups only.
    lines=resume.strip().splitlines(); out=[]; group=[]
    def flush():
        out.extend(sorted(group,key=lambda line:-len(skills(line)&set(r['matched']))));group.clear()
    for line in lines:
        if re.match(r'^\s*[-•*]\s+',line):group.append(line)
        else:flush();out.append(line)
    flush()
    return '\n'.join(out)

def pdf_bytes(title,body):
    buf=BytesIO(); styles=getSampleStyleSheet(); styles['Title'].textColor=HexColor('#49358c'); styles['BodyText'].leading=15
    # Built-in PDF fonts cover Latin text; replace unsupported characters explicitly.
    def safe(s):return escape(s.encode('cp1252','replace').decode('cp1252'))
    story=[Paragraph(safe(title),styles['Title']),Spacer(1,12)]
    for line in body.splitlines():
        story.append(Paragraph(safe(line),styles['BodyText']) if line.strip() else Spacer(1,8))
    SimpleDocTemplate(buf,pagesize=A4,title=title).build(story)
    return buf.getvalue()
