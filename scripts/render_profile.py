from pathlib import Path
from render_card import lettering,font_data
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'

def txt(s,x,y,size,weight,color):
    return lettering(s.replace('&','&'),x,y,size,weight,color)[0].replace(f'aria-label="{s}"',f'aria-label="{escape(s)}"')

def length(s,size,weight='Regular'):
    return font_data(weight)[3].getlength(s)*size/1000

def spaced(s,x,y,size,color,spacing=1.25):
    out=[]
    for c in s:
        if c!=' ':out.append(txt(c,x,y,size,'Medium',color))
        x+=length(c,size,'Medium')+spacing
    return ''.join(out),x

def make(light):
    fg='#1f2328' if light else '#e6edf3'; secondary='#57606a' if light else '#9da7b3'; muted='#57606a' if light else '#a2acb7'; line='#d0d7de' if light else '#353c46'; fill='#f6f8fa' if light else '#171d25'
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="176" viewBox="0 0 1000 176" role="img" aria-labelledby="t d"><title id="t">Exploring agent workflows beyond the interface.</title><desc id="d">I research, experiment and build tools that make agent workflows, decisions and system interactions more transparent and understandable. Research focus: Agent Observability, Tool Execution, Memory and Context, Requests, Local Systems.</desc>']
    svg += [txt('Exploring agent workflows',10,44,36,'SemiBold',fg),txt('beyond the interface.',10,85,36,'SemiBold',fg)]
    svg += [f'<path d="M510 16V90" stroke="{line}" stroke-width="1.2"/>']
    for i,s in enumerate(['I research, experiment and build tools that make','agent workflows, decisions and system interactions','more transparent and understandable.']):
        svg.append(txt(s,536,32+i*24,16.8,'Regular',secondary))
    svg.append(f'<g transform="translate(11 139)" stroke="{muted}" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M0 0 11-6 22 0 11 6Z M0 5 11 11 22 5 M0 10 11 16 22 10"/></g>')
    label,end=spaced('RESEARCH FOCUS',45,149,13,muted,1.1);svg.append(label)
    tags=['Agent Observability','Tool Execution','Memory & Context','Requests','Local Systems']
    widths=[length(s,15,'Medium')+28 for s in tags]; x=200;gap=(990-x-sum(widths))/4
    for s,w in zip(tags,widths):
        svg.append(f'<rect x="{x:.2f}" y="127" width="{w:.2f}" height="34" rx="7" fill="{fill}" stroke="{line}" stroke-width="1"/>');svg.append(txt(s,x+14,149,15,'Medium',fg));x+=w+gap
    svg.append('</svg>')
    section,end=spaced('SELECTED PROJECTS',10,19,14,muted,1.45)
    sec=f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="36" viewBox="0 0 1000 36" role="img" aria-label="Selected projects">{section}<path d="M {end+20:.2f} 14.5 H 990" stroke="{line}" stroke-width="1"/></svg>'
    suffix='light' if light else 'dark'
    (OUT/f'profile-intro-{suffix}.svg').write_text(''.join(svg));(OUT/f'profile-projects-{suffix}.svg').write_text(sec)
if __name__=='__main__':
    make(False);make(True)
