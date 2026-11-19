"""Render the MacCleaner project card using the shared Agent Observer style."""
import argparse, json, os, tempfile, urllib.request
from pathlib import Path
import render_card as base

OUT = Path(__file__).resolve().parents[1] / 'assets'
TITLE = 'MacCleaner'
DESCRIPTION = ['System diagnostics and resource', 'monitoring for macOS.']
# Rear-to-front glass panels; paths extend beyond the card clip.
PANELS = [
    ('M 624 456 L 701 141 Q 704 130 716 124 L 1044 -31 L 1044 456 Z', .62, .20),
    ('M 692 456 L 772 195 Q 775 183 788 177 L 1050 53 L 1050 456 Z', .86, .37),
    ('M 572 456 L 631 293 Q 635 283 647 278 L 1044 92 L 1044 456 Z', .35, .19),
    ('M 805 456 L 855 290 Q 858 279 870 273 L 1044 192 L 1044 456 Z', .72, .25),
    ('M 782 456 L 824 348 Q 828 337 840 331 L 1044 236 L 1044 456 Z', .43, .18),
]
# A fine highlight follows the main panel's rounded upper edge.
GLINT = [(716,393),(735,310),(750,240),(772,195),(775,183),(779,181),(788,177),(850,148),(903,123),(978,87)]

def get_stars():
    req=urllib.request.Request('https://api.github.com/repos/Jas952/MacCleaner',headers={'Accept':'application/vnd.github+json','User-Agent':'Jas952-profile-card','X-GitHub-Api-Version':'2022-11-28'})
    if os.getenv('GITHUB_TOKEN'):req.add_header('Authorization','Bearer '+os.environ['GITHUB_TOKEN'])
    with urllib.request.urlopen(req,timeout=25) as response:return int(json.load(response)['stargazers_count'])

def render_svg(stars):
    original=base.render_svg(None)
    prefix=original.split('<g clip-path="url(#card)">',1)[0]
    prefix=prefix.replace('Agent Observer',TITLE).replace('Visual analysis of AI agent activity: commands, resources, memory and results.','System diagnostics and resource monitoring for macOS.')
    # Use the same card silhouette, background and shadow as Agent Observer.
    defs='''<defs>
      <linearGradient id="glass" gradientUnits="userSpaceOnUse" x1="672" y1="98" x2="974" y2="377">
        <stop stop-color="#a9bfd4" stop-opacity=".05"/><stop offset=".25" stop-color="#a9bfd4" stop-opacity=".24"/><stop offset=".56" stop-color="#7b94ae" stop-opacity=".08"/><stop offset="1" stop-color="#7b94ae" stop-opacity=".025"/>
      </linearGradient>
      <linearGradient id="edge" gradientUnits="userSpaceOnUse" x1="650" y1="365" x2="980" y2="73">
        <stop stop-color="#9eb2c8" stop-opacity=".04"/><stop offset=".46" stop-color="#aebfd1" stop-opacity=".85"/><stop offset="1" stop-color="#aebfd1" stop-opacity=".16"/>
      </linearGradient>
      <radialGradient id="panelglow" gradientUnits="userSpaceOnUse" cx="788" cy="188" r="126">
        <stop stop-color="#9ab9dd" stop-opacity=".14"/><stop offset=".42" stop-color="#9ab9dd" stop-opacity=".05"/><stop offset="1" stop-color="#9ab9dd" stop-opacity="0"/>
      </radialGradient>
    </defs>'''
    panels=''.join(f'<path d="{d}" fill="url(#glass)" fill-opacity="{a}" stroke="url(#edge)" stroke-opacity="{b}" stroke-width="1.8" stroke-linejoin="round"/>' for d,a,b in PANELS)
    art=f'<g clip-path="url(#card)">{panels}<circle cx="788" cy="188" r="126" fill="url(#panelglow)"/></g>'
    icon='<g transform="translate(79 70)" fill="none" stroke="#b4c0cf" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><rect x="1.2" y="1.2" width="34" height="24" rx="3.2"/><path d="M18.2 25.2V32 M11 32H25.4"/></g>'
    title,tb=base.lettering(TITLE,78,179,43,'SemiBold','#edf0f4')
    desc=''.join(base.lettering(line,78,y,24,'Regular','#a3adbd')[0] for line,y in zip(DESCRIPTION,[229,261]))
    lang,lb=base.lettering('Swift',109,350,23,'Regular','#a2acb9');meta_y=(lb[1]+lb[3])/2
    arrow_scale=.90;arrow_x=tb[2]+20;arrow_y=(tb[1]+tb[3])/2-11.5*arrow_scale+1.1
    arrow=f'<g transform="translate({arrow_x:.3f} {arrow_y:.3f}) scale({arrow_scale})" fill="none" stroke="#a2acba" stroke-width="2.25" stroke-linecap="round" stroke-linejoin="round"><path d="M9 1H2Q0 1 0 3V21Q0 23 2 23H20Q22 23 22 21V14 M10 13L23 0 M14 0H23V9"/></g>'
    count=''
    if stars is not None:
        count_text,_=base.lettering(str(stars),257,350,23,'Regular','#a2acb9')
        count=f'<g transform="translate(238 {meta_y:.3f})" fill="none" stroke="#a0a9b7" stroke-width="2.1" stroke-linejoin="round"><path d="M0 -9 2.8 -3.1 9 -2.2 4.5 2.2 5.3 8.3 0 5.4 -5.3 8.3 -4.5 2.2 -9 -2.2 -2.8 -3.1Z"/></g>{count_text}'
    return prefix+defs+art+icon+title+arrow+desc+f'<circle cx="89" cy="{meta_y:.3f}" r="8.2" fill="#748196"/>'+lang+count+'</svg>'

def render(stars):
    OUT.mkdir(exist_ok=True)
    svg=render_svg(stars)
    (OUT/'maccleaner-card.svg').write_text(svg,encoding='utf-8')
    # Reuse the shared lossless 50-fps animation writer without changing its files.
    old_out,old_curves=base.OUT,base.CURVES
    try:
        with tempfile.TemporaryDirectory() as tmp:
            base.OUT=Path(tmp);base.CURVES=[None,None,GLINT]
            base.animate(svg)
            for ext in ['png','webp']:
                (OUT/f'maccleaner-card.{ext}').write_bytes((Path(tmp)/f'agent-observer-card.{ext}').read_bytes())
    finally:
        base.OUT,base.CURVES=old_out,old_curves

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--live',action='store_true');p.add_argument('--stars',type=int);a=p.parse_args()
    render(get_stars() if a.live else a.stars)
