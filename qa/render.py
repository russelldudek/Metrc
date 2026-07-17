from pathlib import Path
import base64
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
css = (root/'brand-tokens.css').read_text() + '\n' + (root/'styles.css').read_text().replace("@import url('./brand-tokens.css');", '')
js = (root/'app.js').read_text()
logo_b64 = base64.b64encode((root/'assets/brand/metrc-logo-forest.png').read_bytes()).decode()
logo_uri = f'data:image/png;base64,{logo_b64}'

def inline_html(name: str) -> str:
    html = (root/name).read_text()
    html = html.replace('<link rel="stylesheet" href="styles.css">', f'<style>{css}</style>')
    html = html.replace('src="assets/brand/metrc-logo-forest.png"', f'src="{logo_uri}"')
    html = html.replace('<script src="app.js"></script>', f'<script>{js}</script>')
    return html

pdf_jobs = {
    'resume.html': 'docs/russell-dudek-metrc-chief-of-staff-resume.pdf',
    'cover-letter.html': 'docs/russell-dudek-metrc-chief-of-staff-cover-letter.pdf',
    'interview-brief.html': 'docs/metrc-chief-of-staff-interview-thesis-brief.pdf',
    '120-day-plan.html': 'docs/metrc-chief-of-staff-first-120-days.pdf',
    'priority-trace-review.html': 'docs/metrc-executive-priority-trace-review.pdf',
}
viewports = [(1440,900,'desktop'),(1280,800,'laptop'),(768,1024,'tablet'),(390,844,'mobile')]
with sync_playwright() as p:
    launch_kwargs = {'headless': True, 'args': ['--no-sandbox', '--disable-dev-shm-usage']}
    chromium_path = Path('/usr/bin/chromium')
    if chromium_path.exists():
        launch_kwargs['executable_path'] = str(chromium_path)
    browser = p.chromium.launch(**launch_kwargs)
    page = browser.new_page()
    for html, out in pdf_jobs.items():
        page.set_content(inline_html(html), wait_until='load')
        page.emulate_media(media='print')
        page.pdf(path=str(root/out), format='Letter', print_background=True, prefer_css_page_size=True, margin={'top':'0','right':'0','bottom':'0','left':'0'})
        print('pdf', out)
    for w,h,name in viewports:
        context = browser.new_context(viewport={'width':w,'height':h}, device_scale_factor=1)
        pg = context.new_page()
        pg.set_content(inline_html('index.html'), wait_until='load')
        pg.screenshot(path=str(root/f'qa/index-{name}.png'), full_page=True)
        print('shot',name,'scroll',pg.evaluate('document.documentElement.scrollWidth'),'client',pg.evaluate('document.documentElement.clientWidth'))
        context.close()
    browser.close()
