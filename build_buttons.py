"""Generate lightweight, self-hosted SVG link buttons for the profile."""
from pathlib import Path
import xml.etree.ElementTree as ET
root = Path(__file__).resolve().parents[1] / 'assets'
root.mkdir(exist_ok=True, parents=True)

def badge(label, slug, accent, icon):
    # No JS, no external fonts, no remote fetches: GitHub-safe static SVG.
    template='''<svg xmlns="http://www.w3.org/2000/svg" width="224" height="58" viewBox="0 0 224 58" role="img" aria-label="{label}">
<defs>
<linearGradient id="bg" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#142238"/><stop offset="1" stop-color="#0B1324"/></linearGradient>
<linearGradient id="acc" x1="0" x2="1"><stop stop-color="{accent}" stop-opacity=".20"/><stop offset="1" stop-color="{accent}" stop-opacity=".01"/></linearGradient>
</defs>
<rect x="1" y="1" width="222" height="56" rx="13" fill="url(#bg)" stroke="{accent}" stroke-opacity=".48" stroke-width="1.3"/>
<path d="M14 2 H90" stroke="{accent}" stroke-width="2.5" stroke-linecap="round"/>
<rect x="12" y="10" width="38" height="38" rx="9" fill="url(#acc)" stroke="{accent}" stroke-opacity=".6" />
{icon}
<text x="61" y="34" font-family="Arial, sans-serif" font-weight="700" font-size="15" letter-spacing="1.5" fill="#ECF6FF">{label}</text>
<path d="M193 24 H206 V37 M206 24 L192 38" fill="none" stroke="{accent}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''
    data=template.format(label=label,accent=accent,icon=icon)
    ET.fromstring(data)
    (root/f'contact_{slug}.svg').write_text(data,encoding='utf-8')

badge('LINKEDIN','linkedin','#69B9FF','''<text x="20" y="38" font-family="Arial, sans-serif" font-weight="bold" font-size="23" fill="#69B9FF">in</text>''')
badge('TELEGRAM','telegram','#5BE3DC','''<path d="M18 29.4 45 18.8 37 41 31.5 33.5 25.2 38 25.9 29.7 41 21.9 28.6 33.1 31.5 33.5" fill="none" stroke="#5BE3DC" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>''')
badge('EMAIL','email','#B8A0FF','''<rect x="19" y="22" width="25" height="17" rx="3" fill="none" stroke="#B8A0FF" stroke-width="2"/><path d="M20.5 24 31.5 32 42.5 24" fill="none" stroke="#B8A0FF" stroke-width="2"/>''')
# Assembly is not AssemblyScript; a custom generic processor symbol avoids a misleading logo.
assembly='''<svg xmlns="http://www.w3.org/2000/svg" width="158" height="28" viewBox="0 0 158 28" role="img" aria-label="Assembly programming">
<rect x="0" y="0" width="158" height="28" rx="5" fill="#5447A9"/>
<path d="M5 0 H39 V28 H5 Q0 28 0 23 V5 Q0 0 5 0" fill="#252D4D"/>
<rect x="13" y="7" width="13" height="13" rx="2" fill="none" stroke="#D8D5FF" stroke-width="1.6"/>
<path d="M17 4 V7 M22 4 V7 M17 20 V23 M22 20 V23 M10 11 H13 M10 16 H13 M26 11 H29 M26 16 H29" stroke="#D8D5FF" stroke-width="1.5" stroke-linecap="round" />
<text x="46" y="18.6" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#FFFFFF" letter-spacing=".6">ASSEMBLY</text>
</svg>'''
ET.fromstring(assembly)
(root/'assembly_badge.svg').write_text(assembly,encoding='utf-8')
print('Built 4 SVG assets in',root)
