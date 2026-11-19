import argparse, bisect, io, json, math, os, urllib.request
from pathlib import Path
from functools import lru_cache

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'
W,H=1000,426
SCALE=2.4
# Asymmetric, diagonally flowing contours inspired by the approved visual.
CURVES=[
[(385,388),(465,337),(500,306),(576,292),(650,279),(649,224),(690,176),(731,128),(816,101),(887,15)],
[(456,387),(524,337),(562,330),(632,311),(702,292),(674,234),(724,189),(774,144),(839,130),(953,15)],
[(519,387),(568,341),(619,331),(684,315),(749,299),(714,240),(776,206),(838,172),(859,116),(988,78)],
[(594,386),(642,353),(700,347),(755,320),(810,293),(767,261),(814,230),(861,199),(880,142),(995,134)],
[(674,386),(720,355),(785,348),(835,321),(885,294),(913,266),(900,231),(887,196),(931,175),(996,191)],
[(762,388),(814,357),(885,349),(932,315),(979,281),(947,253),(956,233),(965,213),(981,211),(995,214)],
[(846,388),(890,358),(945,345),(997,306)],
]
CURVES=[[(x, round(18+(y-18)*380/334,3)) for x,y in curve] for curve in CURVES]
OPACITIES=[.18,.32,.45,.43,.26,.20,.14]

def path_d(p):
    return 'M %s %s '%p[0]+' '.join('C '+' '.join(f'{x} {y}' for x,y in p[i:i+3]) for i in range(1,len(p),3))

def sample(p):
    pts=[]
    for i in range(0,len(p)-1,3):
        a,b,c,d=p[i:i+4]
        for k in range(160):
            t=k/160;u=1-t
            pts.append(tuple(u**3*a[j]+3*u*u*t*b[j]+3*u*t*t*c[j]+t**3*d[j] for j in (0,1)))
    pts.append(p[-1]);return pts

def get_stars():
    req=urllib.request.Request('https://api.github.com/repos/Jas952/agent-observer',headers={'Accept':'application/vnd.github+json','User-Agent':'Jas952-profile-card','X-GitHub-Api-Version':'2022-11-28'})
    if os.getenv('GITHUB_TOKEN'):req.add_header('Authorization','Bearer '+os.environ['GITHUB_TOKEN'])
    with urllib.request.urlopen(req,timeout=25) as response:return int(json.load(response)['stargazers_count'])

# Glyph outlines guarantee identical typography in every SVG renderer.
@lru_cache(maxsize=4)
def font_data(weight):
    from fontTools.ttLib import TTFont
    from PIL import ImageFont
    names=[f'Inter-{weight}.otf',f'Inter-{weight}.ttf']
    paths=[p for root in [Path('/usr/share/fonts'),Path('/usr/local/share/fonts')] if root.exists() for n in names for p in root.rglob(n)]
    if not paths: raise RuntimeError('Install Inter (Ubuntu: fonts-inter) before rendering')
    path=paths[0]; f=TTFont(path)
    return f.getGlyphSet(),f.getBestCmap(),f['head'].unitsPerEm,ImageFont.truetype(str(path),1000)

def lettering(text,x,baseline,size,weight,color):
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.boundsPen import BoundsPen
    gs,cmap,units,pil=font_data(weight); k=size/units
    parts=[]; bounds=[]
    for i,ch in enumerate(text):
        name=cmap[ord(ch)]; xx=x+(pil.getlength(text[:i+1])-pil.getlength(ch))*size/1000
        pen=SVGPathPen(gs);gs[name].draw(pen); d=pen.getCommands()
        if d:
            parts.append(f'<path d="{d}" transform="translate({xx:.4f} {baseline:.4f}) scale({k:.8f} {-k:.8f})"/>')
            bp=BoundsPen(gs);gs[name].draw(bp)
            if bp.bounds:
                a,b,c,e=bp.bounds;bounds.append((xx+a*k,baseline-e*k,xx+c*k,baseline-b*k))
    bbox=(min(b[0] for b in bounds),min(b[1] for b in bounds),max(b[2] for b in bounds),max(b[3] for b in bounds))
    return f'<g fill="{color}" aria-label="{text}">'+''.join(parts)+'</g>',bbox

def graph_icon(x,y):
    # Connectors stop at the node outlines, never cross the hollow interiors.
    r=6.1; sw=3.0; a=(r+sw/2,r+sw/2); b=(r+sw/2+29,r+sw/2+17); c=(r+sw/2,r+sw/2+34)
    bits=[]
    for u,v in [(a,b),(c,b)]:
        d=math.dist(u,v);dx=(v[0]-u[0])/d;dy=(v[1]-u[1])/d
        bits.append(f'<path d="M{u[0]+dx*r:.3f} {u[1]+dy*r:.3f} L{v[0]-dx*r:.3f} {v[1]-dy*r:.3f}" stroke-linecap="butt"/>')
    for cx,cy in (a,b,c):bits.append(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>')
    return f'<g transform="translate({x} {y}) scale(.80)" fill="none" stroke="#b4c0cf" stroke-width="{sw}">'+''.join(bits)+'</g>'

def render_svg(stars):
    paths=''.join(f'<path d="{path_d(p)}" opacity="{a}"/>' for p,a in zip(CURVES,OPACITIES))
    title,tb=lettering('Agent Observer',78,179,43,'SemiBold','#edf0f4')
    desc1,_=lettering('Visual analysis of AI agent activity:',78,229,24,'Regular','#a3adbd')
    desc2,_=lettering('commands, resources, memory and results.',78,261,24,'Regular','#a3adbd')
    lang,lb=lettering('Python',109,350,23,'Regular','#a2acb9')
    meta_y=(lb[1]+lb[3])/2
    arrow_scale=.90
    arrow_x=tb[2]+20; arrow_y=(tb[1]+tb[3])/2-11.5*arrow_scale+1.1
    arrow=f'<g transform="translate({arrow_x:.3f} {arrow_y:.3f}) scale({arrow_scale})" fill="none" stroke="#a2acba" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round"><path d="M9 1H2Q0 1 0 3V21Q0 23 2 23H20Q22 23 22 21V14 M10 13L23 0 M14 0H23V9"/></g>'
    count=''
    if stars is not None:
        count_text,_=lettering(str(stars),257,350,23,'Regular','#a2acb9')
        count=f'<g transform="translate(238 {meta_y:.3f})" fill="none" stroke="#a0a9b7" stroke-width="2.1" stroke-linejoin="round"><path d="M0 -9 2.8 -3.1 9 -2.2 4.5 2.2 5.3 8.3 0 5.4 -5.3 8.3 -4.5 2.2 -9 -2.2 -2.8 -3.1Z"/></g>{count_text}'
    # Approximate a Gaussian shadow with 72 nested vector silhouettes.
    # The alpha approaches zero before reaching the canvas edge.
    layers=[]; previous=0.0
    for i in range(72, -1, -1):
        d=i/4
        target=.25*math.erfc(d/(math.sqrt(2)*5.4))
        alpha=(target-previous)/(1-previous)
        previous=target
        if alpha<.000001: continue
        layers.append(f'<rect x="{20-d:.2f}" y="{21-d:.2f}" width="{960+2*d:.2f}" height="{380+2*d:.2f}" rx="{20+d:.2f}" fill="#010307" opacity="{alpha:.7f}"/>')
    shadow=''.join(layers)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="426" viewBox="0 0 1000 426" role="img" aria-labelledby="title desc">
<title id="title">Agent Observer</title><desc id="desc">Visual analysis of AI agent activity: commands, resources, memory and results.</desc>
<defs>
 <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#171e2a"/><stop offset=".53" stop-color="#111823"/><stop offset="1" stop-color="#141d2b"/></linearGradient>
 <radialGradient id="shade" gradientUnits="userSpaceOnUse" cx="835" cy="276" r="290" gradientTransform="translate(0 60) scale(1 .75)"><stop stop-color="#6f9bc9" stop-opacity=".08"/><stop offset="1" stop-color="#6f9bc9" stop-opacity="0"/></radialGradient>
 <radialGradient id="glow" gradientUnits="userSpaceOnUse" cx="857" cy="273" r="40"><stop stop-color="#a4c9f0" stop-opacity=".32"/><stop offset=".20" stop-color="#a4c9f0" stop-opacity=".12"/><stop offset="1" stop-color="#a4c9f0" stop-opacity="0"/></radialGradient>
 <linearGradient id="contour" gradientUnits="userSpaceOnUse" x1="400" y1="0" x2="980" y2="0"><stop stop-color="#7f9ab6" stop-opacity="0"/><stop offset=".38" stop-color="#8ca6c5" stop-opacity=".40"/><stop offset=".72" stop-color="#a2b8d1" stop-opacity=".8"/><stop offset="1" stop-color="#a2b8d1" stop-opacity=".55"/></linearGradient>
 <clipPath id="card"><rect x="20" y="18" width="960" height="380" rx="20"/></clipPath>
</defs>
{shadow}
<rect x="20" y="18" width="960" height="380" rx="20" fill="url(#bg)"/>
<g clip-path="url(#card)">
 <ellipse cx="835" cy="276" rx="290" ry="220" fill="url(#shade)"/>
 <g fill="none" stroke="url(#contour)" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round">{paths}</g>
 <path d="M813 270 C794 252 806 234 823 221 C843 205 872 203 887 218 C906 237 893 257 874 268 C850 282 825 282 813 270 Z" fill="none" stroke="#88a3c0" stroke-opacity=".085" stroke-width="1.05" transform="translate(0 31) translate(857 242) scale(.78) translate(-857 -242)"/>
 <circle cx="857" cy="273" r="40" fill="url(#glow)"/><circle cx="857" cy="273" r="5.2" fill="#d2e5f9"/>
</g>
{graph_icon(79,70)}
{title}{arrow}{desc1}{desc2}
<circle cx="89" cy="{meta_y:.3f}" r="8.2" fill="#748196"/>{lang}{count}
</svg>''' 

def animate(svg):
    import cairosvg
    from PIL import Image, ImageDraw, ImageFilter
    size=(round(W*SCALE),round(H*SCALE))
    base=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=size[0],output_height=size[1]))).convert('RGBA')
    base.save(OUT/'agent-observer-card.png')
    pts=sample(CURVES[2]);distances=[0.]
    for p,q in zip(pts,pts[1:]):distances.append(distances[-1]+math.dist(p,q))
    def at(d):
        i=max(0,min(len(pts)-2,bisect.bisect_right(distances,d)-1));f=(d-distances[i])/(distances[i+1]-distances[i]);return tuple(pts[i][j]+f*(pts[i+1][j]-pts[i][j]) for j in (0,1))
    start,end=110,distances[-1]-100
    # Build a standards-compliant animated WebP from lossless VP8L subframes.
    # Only the current and previous highlight rectangle changes; no full-frame
    # re-encoding, no lossy quantization, and no opaque background matte.
    import struct
    def u24(n):return int(n).to_bytes(3,'little')
    def chunk(tag,data):return tag+struct.pack('<I',len(data))+data+(b'\0' if len(data)%2 else b'')
    def vp8l(im):
        buf=io.BytesIO();im.save(buf,format='WEBP',lossless=True,quality=90,method=1,exact=True)
        raw=buf.getvalue();off=12
        while off+8<=len(raw):
            tag=raw[off:off+4];n=struct.unpack_from('<I',raw,off+4)[0]
            if tag==b'VP8L':return chunk(tag,raw[off+8:off+8+n])
            off+=8+n+(n%2)
        raise RuntimeError('Lossless WebP payload not found')
    def anmf(im,x,y,ms):
        assert x%2==0 and y%2==0
        return chunk(b'ANMF',u24(x//2)+u24(y//2)+u24(im.width-1)+u24(im.height-1)+u24(ms)+b'\x02'+vp8l(im))
    body=[chunk(b'VP8X',b'\x12\0\0\0'+u24(size[0]-1)+u24(size[1]-1)),chunk(b'ANIM',b'\0'*6),anmf(base,0,0,20)]
    prev=None
    for i in range(1,90):
        u=i/89;d=start+(end-start)*u;strength=math.sin(math.pi*u)**.75
        xy=[at(max(0,d-56+j*56/36)) for j in range(37)]
        x0=max(0,int(min(p[0] for p in xy)*SCALE)-25);y0=max(0,int(min(p[1] for p in xy)*SCALE)-25)
        x1=min(size[0],int(max(p[0] for p in xy)*SCALE)+26);y1=min(size[1],int(max(p[1] for p in xy)*SCALE)+26)
        glow=Image.new('RGBA',(x1-x0,y1-y0));dr=ImageDraw.Draw(glow)
        for j in range(36):
            f=(j+.5)/36;alpha=round(155*strength*math.sin(math.pi*f)**1.5)
            dr.line([(round(x*SCALE-x0),round(y*SCALE-y0)) for x,y in xy[j:j+2]],fill=(198,222,249,alpha),width=4)
        combined=Image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(4.2)),glow)
        box=(x0,y0,x1,y1); old=prev or box
        x=min(x0,old[0])//2*2;y=min(y0,old[1])//2*2
        right=max(x1,old[2]);bottom=max(y1,old[3])
        tile=base.crop((x,y,right,bottom));tile.alpha_composite(combined,(x0-x,y0-y))
        body.append(anmf(tile,x,y,620 if i==89 else 20));prev=box
    data=b'WEBP'+b''.join(body)
    (OUT/'agent-observer-card.webp').write_bytes(b'RIFF'+struct.pack('<I',len(data))+data)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--live',action='store_true');p.add_argument('--stars',type=int);p.add_argument('--animate',action='store_true');a=p.parse_args()
    stars=get_stars() if a.live else a.stars
    OUT.mkdir(exist_ok=True);svg=render_svg(stars);(OUT/'agent-observer-card.svg').write_text(svg,encoding='utf-8')
    if a.animate:animate(svg)
