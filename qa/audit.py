from pathlib import Path
import base64, re, subprocess, sys
from bs4 import BeautifulSoup
from pypdf import PdfReader
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
html_files=['index.html','resume.html','cover-letter.html','interview-brief.html','120-day-plan.html','priority-trace-review.html']
css=(root/'brand-tokens.css').read_text()+"\n"+(root/'styles.css').read_text().replace("@import url('./brand-tokens.css');",'')
js=(root/'app.js').read_text()
logo=base64.b64encode((root/'assets/brand/metrc-logo-forest.png').read_bytes()).decode()

def inline(name):
    s=(root/name).read_text()
    s=s.replace('<link rel="stylesheet" href="styles.css">',f'<style>{css}</style>')
    s=s.replace('src="assets/brand/metrc-logo-forest.png"',f'src="data:image/png;base64,{logo}"')
    s=s.replace('<script src="app.js"></script>',f'<script>{js}</script>')
    return s

issues=[]
# Static links and confidentiality
for name in html_files:
    text=(root/name).read_text()
    low=text.lower()
    for forbidden in ['roleforge','github.com/russelldudek/metrc','public repository']:
        if forbidden in low: issues.append(f'{name}: forbidden public string {forbidden}')
    soup=BeautifulSoup(text,'html.parser')
    for tag in soup.find_all(['a','img']):
        attr='href' if tag.name=='a' else 'src'
        v=tag.get(attr,'')
        if not v or v.startswith(('#','mailto:','tel:','http://','https://','data:','javascript:')): continue
        target=(root/v.split('#')[0].split('?')[0]).resolve()
        if not target.exists(): issues.append(f'{name}: missing local target {v}')
    imgs=soup.select('img[src*="metrc-logo-forest"]')
    if len(imgs)!=1: issues.append(f'{name}: expected exactly one official Metrc logo, got {len(imgs)}')

if 'View Cover Letter' not in (root/'resume.html').read_text(): issues.append('resume missing View Cover Letter')
if 'View Resume' not in (root/'cover-letter.html').read_text(): issues.append('cover letter missing View Resume')
if 'https://russelldudek.github.io/Metrc/' not in (root/'resume.html').read_text(): issues.append('resume missing visible candidate URL')

# PDFs
expected={
'docs/russell-dudek-metrc-chief-of-staff-resume.pdf':2,
'docs/russell-dudek-metrc-chief-of-staff-cover-letter.pdf':1,
'docs/metrc-chief-of-staff-interview-thesis-brief.pdf':4,
'docs/metrc-chief-of-staff-first-120-days.pdf':4,
'docs/metrc-executive-priority-trace-review.pdf':2,
}
for rel,pages in expected.items():
    p=root/rel
    r=PdfReader(str(p))
    if len(r.pages)!=pages: issues.append(f'{rel}: pages {len(r.pages)} != {pages}')
    for i,pg in enumerate(r.pages,1):
        box=pg.mediabox
        w,h=float(box.width),float(box.height)
        if abs(w-612)>1 or abs(h-792)>1: issues.append(f'{rel} p{i}: not Letter {w}x{h}')
    txt='\n'.join((pg.extract_text() or '') for pg in r.pages).lower()
    for forbidden in ['roleforge','github.com/russelldudek/metrc','public repository']:
        if forbidden in txt: issues.append(f'{rel}: forbidden PDF string {forbidden}')
    if 'russelldudek.github.io/metrc/' not in txt: issues.append(f'{rel}: candidate URL missing from PDF text')

# Browser geometry
with sync_playwright() as p:
    launch_kwargs={'headless':True,'args':['--no-sandbox','--disable-dev-shm-usage']}
    chromium_path=Path('/usr/bin/chromium')
    if chromium_path.exists():
        launch_kwargs['executable_path']=str(chromium_path)
    b=p.chromium.launch(**launch_kwargs)
    for name in html_files:
        for w,h,label in [(1440,900,'desktop'),(768,1024,'tablet'),(390,844,'mobile'),(320,800,'narrow')]:
            pg=b.new_page(viewport={'width':w,'height':h})
            errs=[]; pg.on('pageerror',lambda e, arr=errs: arr.append(str(e)))
            pg.set_content(inline(name),wait_until='load')
            geom=pg.evaluate('''() => ({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,
                pages:[...document.querySelectorAll('.doc-page')].map(x=>({sw:x.scrollWidth,cw:x.clientWidth,sh:x.scrollHeight,ch:x.clientHeight}))})''')
            if geom['sw']>geom['cw']+1: issues.append(f'{name} {label}: horizontal overflow {geom["sw"]}>{geom["cw"]}')
            for j,g in enumerate(geom['pages'],1):
                if g['sw']>g['cw']+1: issues.append(f'{name} {label} page{j}: sheet horizontal overflow')
                if label in ('tablet','mobile','narrow') and g['sh']>g['ch']+2: issues.append(f'{name} {label} page{j}: screen sheet clipping {g["sh"]}>{g["ch"]}')
            if errs: issues.append(f'{name} {label}: JS errors {errs}')
            pg.close()
        if name!='index.html':
            pg=b.new_page(viewport={'width':1440,'height':900})
            pg.set_content(inline(name),wait_until='load'); pg.emulate_media(media='print')
            results=pg.evaluate('''() => [...document.querySelectorAll('.doc-page')].map((page,idx)=>{
              const footer=page.querySelector('.doc-footer'); const ft=footer?footer.getBoundingClientRect().top:page.getBoundingClientRect().bottom;
              const kids=[...page.children].filter(x=>!x.classList.contains('doc-footer'));
              const max=Math.max(...kids.map(x=>x.getBoundingClientRect().bottom));
              const sizes=[...page.querySelectorAll('p,li,td,.trace-sheet-value')].map(x=>parseFloat(getComputedStyle(x).fontSize)).filter(Number.isFinite);
              return {idx:idx+1,gap:ft-max,minfont:sizes.length?Math.min(...sizes):99,max:max,footer:ft};
            })''')
            for r in results:
                if r['gap']<2: issues.append(f'{name} print page{r["idx"]}: content/footer collision gap={r["gap"]:.1f}px')
                if r['minfont']<8: issues.append(f'{name} print page{r["idx"]}: min main font {r["minfont"]:.1f}px')
            pg.close()
    b.close()

print('AUDIT', 'PASS' if not issues else 'FAIL')
for i in issues: print('-',i)
sys.exit(1 if issues else 0)
