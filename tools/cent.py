import re,glob,numpy as np
from PIL import Image
V='v/'
G='/sessions/'+__import__('os').environ['HOME'].split('/')[-1]+'/mnt/Hearts of Iron IV/'
import os; G=os.environ['HOME']+'/mnt/Hearts of Iron IV/'
img=np.array(Image.open(G+'map/provinces.bmp').convert('RGB'))
H,W,_=img.shape
key=(img[:,:,0].astype(np.int64)<<16)|(img[:,:,1].astype(np.int64)<<8)|img[:,:,2]
col2id={}
for line in open(V+'map/definition.csv',encoding='latin-1'):
    p=line.split(';')
    if len(p)<4 or not p[0].isdigit(): continue
    col2id[(int(p[1])<<16)|(int(p[2])<<8)|int(p[3])]=int(p[0])
flat=key.ravel()
u,inv=np.unique(flat,return_inverse=True)
ys,xs=np.divmod(np.arange(flat.size),W)
cnt=np.bincount(inv); sx=np.bincount(inv,xs); sy=np.bincount(inv,ys)
pc={}
for i,c in enumerate(u):
    if c in col2id: pc[col2id[c]]=(sx[i]/cnt[i],sy[i]/cnt[i],cnt[i])
names={}
for l in open(V+'localisation/english/state_names_l_english.yml',encoding='utf-8-sig'):
    m=re.match(r'\s*(STATE_\d+):\d*\s*"(.*)"',l)
    if m: names[m.group(1)]=m.group(2)
out=open('states.tsv','w')
for f in glob.glob(V+'history/states/*.txt'):
    t=open(f,encoding='utf-8-sig',errors='replace').read()
    sid=int(re.search(r'\bid\s*=\s*(\d+)',t).group(1))
    nm=re.search(r'name\s*=\s*"(\w+)"',t).group(1)
    own=re.search(r'owner\s*=\s*(\w+)',t); own=own.group(1) if own else '-'
    cat=re.search(r'state_category\s*=\s*(\w+)',t); cat=cat.group(1) if cat else '-'
    prov=[int(x) for x in re.search(r'provinces\s*=\s*\{([^}]*)\}',t).group(1).split()]
    tx=ty=tn=0
    for p in prov:
        if p in pc: x,y,n=pc[p]; tx+=x*n; ty+=y*n; tn+=n
    cx,cy=(tx/tn,ty/tn) if tn else (-1,-1)
    out.write(f"{sid}\t{names.get(nm,nm)}\t{own}\t{cat}\t{cx:.0f}\t{H-cy:.0f}\t{os.path.basename(f)}\n")
print(W,H)
