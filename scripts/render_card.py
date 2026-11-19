import argparse, io, json, math, os, urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'
W,H=1000,440
RADII=[47,78,112,150,193,239,288,340,396]

def point(r,t):
    c=math.cos(t); s=math.sin(t)
    # Irregular, nested contour lines with an oblique axis.
    m=1+0.10*math.sin(3*t+.8)+0.055*math.cos(5*t-.4)
    return 899+r*m*(c+.23*s), 266+r*m*(.82*s-.17*c)

def curve(r):
    p=[point(r,i*math.tau/240) for i in range(241)]
    return 'M'+' L'.join(f'{x:.2f} {y:.2f}' for x,y in p)+' Z'

def get_stars():
    req=urllib.request.Request('https://api.github.com/repos/Jas952/agent-observer',headers={'Accept':'application/vnd.github+json','User-Agent':'Jas952-profile-card','X-GitHub-Api-Version':'2022-11-28'})
    if os.getenv('GITHUB_TOKEN'):req.add_header('Authorization','Bearer '+os.environ['GITHUB_TOKEN'])
    with urllib.request.urlopen(req,timeout=25) as response:
        return int(json.load(response)['stargazers_count'])

def render_svg(stars):
    paths=''.join(f'<path d="{curve(r)}" opacity="{a}"/>' for r,a in zip(RADII,[.32,.52,.68,.65,.52,.43,.28,.19,.10]))
    count='' if stars is None else f'''<g transform="translate(270 363)" fill="none" stroke="#a8a8a8" stroke-width="2.6" stroke-linejoin="round"><path d="M0 -12 3.7 -4.1 12 -3 6 3 7.1 11 0 7 -7.1 11 -6 3 -12 -3 -3.7 -4.1Z"/></g><text x="294" y="372" font-size="27" fill="#b9b9b9">{stars}</text>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="440" viewBox="0 0 1000 440" role="img" aria-labelledby="title desc">
<title id="title">Agent Observer</title><desc id="desc">Visual analysis of AI agent activity: commands, resources, memory and results.</desc>
<defs>
 <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#111112"/><stop offset="1" stop-color="#0b0b0c"/></linearGradient>
 <radialGradient id="glow"><stop stop-color="#e5e5e5" stop-opacity=".17"/><stop offset=".36" stop-color="#bcbcbc" stop-opacity=".055"/><stop offset="1" stop-color="#bcbcbc" stop-opacity="0"/></radialGradient>
 <linearGradient id="contour" gradientUnits="userSpaceOnUse" x1="610" y1="0" x2="980" y2="0"><stop stop-color="#969698" stop-opacity="0"/><stop offset=".38" stop-color="#969698" stop-opacity=".52"/><stop offset=".8" stop-color="#969698"/><stop offset="1" stop-color="#969698"/></linearGradient>
 <clipPath id="clip"><rect x="1" y="1" width="998" height="438" rx="21"/></clipPath>
</defs>
<rect x="1.5" y="1.5" width="997" height="437" rx="21" fill="url(#bg)" stroke="#424244" stroke-width="3"/>
<g clip-path="url(#clip)">
 <g fill="none" stroke="url(#contour)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">{paths}</g>
 <circle cx="899" cy="266" r="76" fill="url(#glow)"/>
 <circle cx="899" cy="266" r="5.5" fill="#e4e4e4"/>
</g>
<g transform="translate(68 67)" fill="none" stroke="#dedede" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">
 <path d="M3 0 17 15 3 34 M17 15 38 6 M17 15 38 29 M3 0 3 34" stroke="#a7a7a7"/>
 <g fill="#111112"><circle cx="3" cy="0" r="5.6"/><circle cx="17" cy="15" r="5.6"/><circle cx="3" cy="34" r="5.6"/><circle cx="38" cy="6" r="5.6"/><circle cx="38" cy="29" r="5.6"/></g>
</g>
<g font-family="Arial, Helvetica, sans-serif">
 <text x="62" y="171" font-size="49" font-weight="700" letter-spacing="-1.4" fill="#f0f0f0">Agent Observer</text>
 <g transform="translate(429 141)" stroke="#9d9d9d" stroke-width="2.8" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M13 0H0V26H26V13 M11 15L26 0 M16 0H26V10"/></g>
 <text x="63" y="230" font-size="29" fill="#b5b5b5">Visual analysis of AI agent activity:</text>
 <text x="63" y="272" font-size="29" fill="#b5b5b5">commands, resources, memory and results.</text>
 <circle cx="74" cy="363" r="9" fill="#a1a1a1"/><text x="95" y="372" font-size="27" fill="#b9b9b9">Python</text>
 {count}
</g></svg>'''

def animate(svg):
    import cairosvg
    from PIL import Image,ImageDraw,ImageFilter
    scale=1.5
    base=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=int(W*scale),output_height=int(H*scale)))).convert('RGB')
    base.save(OUT/'agent-observer-card.png')
    frames=[]; durations=[]
    # Fixed geometry; sweep a small soft highlight along one contour.
    for i in range(100):
        u=i/99; t=2.38+2.18*u
        strength=math.sin(math.pi*u)**.65
        glow=Image.new('RGBA',base.size);draw=ImageDraw.Draw(glow)
        for j in range(26):
            f=j/25; a=t-.24+f*.24; b=a+.011
            p=[point(193,a),point(193,b)]
            alpha=int(153*strength*math.sin(math.pi*f)**1.15)
            draw.line([(round(x*scale),round(y*scale)) for x,y in p],fill=(245,245,245,alpha),width=3)
        halo=glow.filter(ImageFilter.GaussianBlur(3.2)); frame=Image.alpha_composite(base.convert('RGBA'),halo);frame=Image.alpha_composite(frame,glow)
        frames.append(frame.convert('RGB'));durations.append(20)
    durations[-1]+=850
    frames[0].save(OUT/'agent-observer-card.webp',save_all=True,append_images=frames[1:],duration=durations,loop=0,lossless=True,method=3)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--live',action='store_true');p.add_argument('--stars',type=int);p.add_argument('--animate',action='store_true');a=p.parse_args()
    stars=get_stars() if a.live else a.stars
    OUT.mkdir(exist_ok=True);svg=render_svg(stars);(OUT/'agent-observer-card.svg').write_text(svg,encoding='utf-8')
    if a.animate:animate(svg)
