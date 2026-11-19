import argparse, datetime as dt, hashlib, io, json, math, os, struct, urllib.request, urllib.parse
from pathlib import Path
from xml.sax.saxutils import escape
import numpy as np
from PIL import Image, ImageDraw
OUT=Path(__file__).resolve().parents[1]/'assets/fingerprint'; USER='Jas952'
GROUPS=[('AI Agent Systems','#719FDF',['agent-observer','openclaw-my-setup','codex-status-bar']),('Native & Browser Apps','#65C0A4',['MacCleaner','BrowserMonitor','DockShelf']),('Data & Monitoring','#D7B16F',['aggregator-AI-news','flashnet-market-monitor','dashboard-servers']),('Other Projects','#AE91CF',[])]
SIZE=800; FPS=60; SECONDS=12; FRAMES=FPS*SECONDS

def pages(path,params):
    for page in range(1,10001):
        req=urllib.request.Request('https://api.github.com'+path+'?'+urllib.parse.urlencode({**params,'page':page,'per_page':100}),headers={'Accept':'application/vnd.github+json','User-Agent':'Jas952-fingerprint','X-GitHub-Api-Version':'2022-11-28'})
        if os.getenv('GITHUB_TOKEN'):req.add_header('Authorization','Bearer '+os.environ['GITHUB_TOKEN'])
        with urllib.request.urlopen(req,timeout=45) as r: rows=json.load(r)
        if not isinstance(rows,list):raise RuntimeError('Unexpected API response')
        yield from rows
        if len(rows)<100:return
    raise RuntimeError('Pagination limit reached')

def fetch():
    now=dt.datetime.now(dt.timezone.utc);since=now-dt.timedelta(days=365)
    iso=lambda t:t.isoformat(timespec='seconds').replace('+00:00','Z')
    repos=[r for r in pages('/users/'+USER+'/repos',{'type':'owner'}) if not r['fork'] and not r['private'] and r['name'].lower()!=USER.lower()]
    data={}
    for r in repos:
        n=r['name'];data[n]=[]
        if not r.get('size'):continue
        data[n]=[c['sha'] for c in pages('/repos/'+r['full_name']+'/commits',{'sha':r['default_branch'],'author':USER,'since':iso(since),'until':iso(now)})]
    return now.date().isoformat(),data

def snapshot():
    counts={'agent-observer':63,'MacCleaner':66,'BrowserMonitor':62,'DockShelf':22,'codex-status-bar':24,'openclaw-my-setup':24,'aggregator-AI-news':7,'flashnet-market-monitor':3,'dashboard-servers':9,'books-ai':24,'x-search':8,'llmcalculator_learning':3,'ai-search-for-go-profession':4,'deleter':15}
    return '2026-11-19',{n:[f'{n}:{i}' for i in range(k)] for n,k in counts.items()}

def particles(data):
    buckets=[[] for _ in GROUPS]
    for repo,commits in sorted(data.items()):
        k=next((i for i,(_,_,names) in enumerate(GROUPS) if repo.lower() in [n.lower() for n in names]),3)
        buckets[k].extend((repo,sha) for sha in sorted(commits))
    counts=[len(v) for v in buckets];total=sum(counts);rows=[];offset=0
    for k,items in enumerate(buckets):
        span=math.tau*len(items)/max(1,total)
        for i,(repo,sha) in enumerate(items):
            rng=np.random.default_rng(int.from_bytes(hashlib.sha256((repo+sha).encode()).digest()[:8],'little'))
            a=offset+span*(i+rng.uniform(.05,.95))/len(items)
            y=2*((i*.61803398875+rng.uniform(0,.08))%1)-1
            radial=.27+.73*rng.random()**(1/3)
            if i%5==0:radial=.94+.06*rng.random()
            rr=math.sqrt(1-y*y)*radial
            rows.append((rr*math.cos(a),y*radial,rr*math.sin(a),k))
        offset+=span
    return np.array(rows).reshape((-1,4)),counts

def frame(p,phase):
    im=Image.new('RGBA',(SIZE,SIZE));d=ImageDraw.Draw(im)
    a=phase+.65;co,si=math.cos(a),math.sin(a)
    x=p[:,0]*co+p[:,2]*si;z=-p[:,0]*si+p[:,2]*co
    tilt=.39;y=p[:,1]*math.cos(tilt)-z*math.sin(tilt);z=p[:,1]*math.sin(tilt)+z*math.cos(tilt)
    persp=2.75/(2.75-z);X=SIZE/2+x*312*persp;Y=SIZE/2-y*312*persp
    for i in np.argsort(z):
        t=float(np.clip((z[i]+1)/2,0,1));c=tuple(bytes.fromhex(GROUPS[int(p[i,3])][1][1:]));cx,cy=X[i],Y[i];r=(1.8+4.4*t)*persp[i];alpha=int(40+215*t**1.12)
        if t>.65:
            for factor,op in [(2.1,8),(1.6,14),(1.3,24)]:
                q=r*factor;d.ellipse((cx-q,cy-q,cx+q,cy+q),fill=(*c,op))
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(*c,alpha))
        if t>.79:
            q=r*.25;light=tuple(int(v+(255-v)*.32) for v in c);d.ellipse((cx-q-r*.15,cy-q-r*.15,cx+q-r*.15,cy+q-r*.15),fill=(*light,min(255,alpha+12)))
    return im

def chunk(tag,b):return tag+struct.pack('<I',len(b))+b+(b'\0' if len(b)%2 else b'')
def u24(n):return int(n).to_bytes(3,'little')
def payload(im):
    f=io.BytesIO();im.save(f,format='WEBP',lossless=True,quality=70,method=1,exact=False)
    raw=f.getvalue();pos=12;out=[]
    while pos+8<=len(raw):
        tag=raw[pos:pos+4];n=struct.unpack_from('<I',raw,pos+4)[0]
        if tag in (b'ALPH',b'VP8 ',b'VP8L'):out.append(chunk(tag,raw[pos+8:pos+8+n]))
        pos+=8+n+n%2
    return b''.join(out)

def animate(p):
    body=[chunk(b'VP8X',b'\x12\0\0\0'+u24(SIZE-1)+u24(SIZE-1)),chunk(b'ANIM',b'\0'*6)]
    for i in range(FRAMES):
        im=frame(p,math.tau*i/FRAMES)
        body.append(chunk(b'ANMF',u24(0)+u24(0)+u24(SIZE-1)+u24(SIZE-1)+u24(round((i+1)*1000/FPS)-round(i*1000/FPS))+b'\x02'+payload(im)))
    data=b'WEBP'+b''.join(body);(OUT/'commit-cloud.webp').write_bytes(b'RIFF'+struct.pack('<I',len(data))+data)

def legend(date,data,counts,light):
    fg='#1f2328' if light else '#e6edf3';muted='#59636e' if light else '#8b949e';rule='#d0d7de' if light else '#30363d';total=sum(counts)
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="750" viewBox="0 0 1000 750" role="img" aria-label="Development fingerprint: {total} commits by category"><g font-family="Inter,Arial,sans-serif">',f'<text x="45" y="64" fill="{muted}" font-size="26" letter-spacing="4">DEVELOPMENT FINGERPRINT</text>',f'<path d="M45 88H950" stroke="{rule}" stroke-width="2"/>',f'<text x="39" y="213" font-size="122" font-weight="600" fill="{fg}">{total:,}</text>',f'<text x="47" y="263" font-size="25" letter-spacing="4" fill="{muted}">COMMITS / LAST 12 MONTHS</text>']
    for i,(n,c,_) in enumerate(GROUPS):
        v=counts[i];pct=100*v/max(1,total);y=321+i*88
        s.extend([f'<circle cx="56" cy="{y-9}" r="9" fill="{c}"/>',f'<text x="83" y="{y}" fill="{fg}" font-size="32" font-weight="500">{escape(n)}</text>',f'<text x="950" y="{y}" text-anchor="end" font-size="32" fill="{fg}">{pct:.1f}%</text>',f'<text x="83" y="{y+29}" font-size="23" fill="{muted}">{v:,} commits</text>'])
    s += [f'<path d="M45 654H950" stroke="{rule}" stroke-width="2"/>',f'<text x="45" y="692" fill="{muted}" font-size="23">{len(data)} public repositories </text>',f'<text x="45" y="725" fill="{muted}" font-size="19">Updated {date} · default branches</text></g></svg>']
    (OUT/f'legend-{"light" if light else "dark"}.svg').write_text(''.join(s))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--live',action='store_true');ap.add_argument('--static',action='store_true');args=ap.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    date,data=fetch() if args.live else snapshot();p,counts=particles(data)
    for light in [False,True]:legend(date,data,counts,light)
    frame(p,0).save(OUT/'commit-cloud.png')
    if not args.static:animate(p)
    print('Counts:',counts,'total',sum(counts))
