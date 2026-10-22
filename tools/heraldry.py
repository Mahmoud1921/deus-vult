# Heraldic flags for every tag. draw_flag(tag, w, h) returns an RGBA image of any size,
# so the same design is used for the 82x52 flag and the small shield on leader portraits.
import math
from PIL import Image, ImageDraw, ImageFilter

OR=(230,178,40); ARG=(244,242,234); GUL=(185,30,36); AZ=(32,72,160); VERT=(28,118,62)
SAB=(28,26,26); PURP=(112,38,108); TEAL=(28,140,140); BRN=(120,70,40); MAROON=(120,25,40)
SAFF=(235,140,30); SKY=(110,170,220); TAN=(205,180,130); OLIVE=(110,120,40)

class Canvas:
    def __init__(self,w,h,s=8):
        self.w,self.h,self.s=w,h,s
        self.img=Image.new('RGBA',(w*s,h*s),(0,0,0,255))
        self.u=min(w,h)/2
    def P(self,x,y): return (x*self.w*self.s,y*self.h*self.s)
    def mask(self): m=Image.new('L',self.img.size,0); return m,ImageDraw.Draw(m)
    def paint(self,m,col,outline=None):
        if outline:
            k=max(3,int(self.s*1.2)|1)
            o=m.filter(ImageFilter.MaxFilter(k))
            self.img.paste(outline+(255,),(0,0),o)
        self.img.paste(col+(255,),(0,0),m)
    # fields
    def field(self,col): self.img.paste(col+(255,),(0,0,*self.img.size))
    def rect(self,x0,y0,x1,y1,col):
        m,d=self.mask(); d.rectangle([*self.P(x0,y0),*self.P(x1,y1)],fill=255); self.paint(m,col)
    def hstripes(self,cols,y0=0,y1=1):
        n=len(cols)
        for i,c in enumerate(cols): self.rect(0,y0+(y1-y0)*i/n,1,y0+(y1-y0)*(i+1)/n,c)
    def vstripes(self,cols,x0=0,x1=1):
        n=len(cols)
        for i,c in enumerate(cols): self.rect(x0+(x1-x0)*i/n,0,x0+(x1-x0)*(i+1)/n,1,c)
    def bordure(self,col,t=0.08):
        tw=t*self.u/self.w; th=t*self.u/self.h
        self.rect(0,0,1,th,col); self.rect(0,1-th,1,1,col); self.rect(0,0,tw,1,col); self.rect(1-tw,0,1,1,col)
    def charge(self,fn,cx=.5,cy=.5,size=.8,col=OR,ang=0,flip=False,outline=SAB,**kw):
        m,d=self.mask(); fn(Pen(self,d,cx,cy,size,ang,flip),**kw); self.paint(m,col,outline)

class Pen:
    """Draws into a mask in a local [-1,1] box centred on (cx,cy), size = half-height as a share of the short side."""
    def __init__(self,c,d,cx,cy,size,ang,flip):
        self.c,self.d=c,d; self.ox,self.oy=c.P(cx,cy); self.k=size*c.u*c.s
        self.ca,self.sa=math.cos(math.radians(ang)),math.sin(math.radians(ang)); self.f=-1 if flip else 1
    def t(self,x,y):
        x*=self.f; return (self.ox+(x*self.ca-y*self.sa)*self.k, self.oy+(x*self.sa+y*self.ca)*self.k)
    def poly(self,pts,fill=255): self.d.polygon([self.t(*p) for p in pts],fill=fill)
    def circ(self,x,y,r,fill=255):
        X,Y=self.t(x,y); R=r*self.k; self.d.ellipse([X-R,Y-R,X+R,Y+R],fill=fill)
    def ell(self,x,y,rx,ry,fill=255):
        n=32; self.poly([(x+rx*math.cos(2*math.pi*i/n),y+ry*math.sin(2*math.pi*i/n)) for i in range(n)],fill)
    def line(self,pts,w,fill=255):
        P=[self.t(*p) for p in pts]; W=w*self.k
        self.d.line(P,fill=fill,width=max(1,int(W)),joint='curve')
        for X,Y in (P[0],P[-1]): self.d.ellipse([X-W/2,Y-W/2,X+W/2,Y+W/2],fill=fill)
    def rect(self,x0,y0,x1,y1,fill=255): self.poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],fill)
    def ring(self,x,y,r,w): self.circ(x,y,r); self.circ(x,y,r-w,0)

# ---- charges, drawn in a [-1,1] box
def lion(p,crown=False,axe=False):
    p.line([(.05,.35),(-.12,-.2)],.42)               # body
    p.circ(-.17,-.45,.27)                             # mane
    p.ell(-.4,-.47,.15,.1)                            # muzzle
    p.poly([(-.05,-.68),(.02,-.85),(-.15,-.72)])      # ear
    p.line([(-.2,-.2),(-.55,-.22),(-.68,-.48)],.11)   # forelegs
    p.line([(-.08,-.02),(-.5,.08),(-.66,-.08)],.11)
    p.line([(.0,.45),(-.3,.62),(-.45,.9)],.15)        # hind legs
    p.line([(.15,.4),(.35,.7),(.15,.95)],.15)
    p.line([(.22,.42),(.55,.3),(.6,-.1),(.45,-.4),(.6,-.62)],.07)  # tail
    p.circ(.62,-.66,.09)
    if crown: p.poly([(-.38,-.7),(-.38,-.86),(-.3,-.78),(-.2,-.92),(-.1,-.78),(-.02,-.86),(-.02,-.7)])
    if axe:
        p.line([(-.7,-.42),(-.55,.7)],.06); p.poly([(-.72,-.3),(-.98,-.42),(-.95,-.05),(-.68,-.12)])

def lion_passant(p,wings=False):
    p.line([(-.42,0),(.35,.02)],.34)
    p.circ(-.58,-.2,.22); p.circ(-.68,-.18,.12)
    p.line([(-.4,.08),(-.68,.18),(-.78,.0)],.1)
    p.line([(-.22,.1),(-.28,.5)],.11); p.line([(.18,.1),(.1,.5)],.11); p.line([(.34,.1),(.44,.5)],.11)
    p.line([(.4,-.05),(.62,-.35),(.45,-.55),(.55,-.72)],.07); p.circ(.57,-.75,.09)
    if wings: p.poly([(-.25,-.1),(-.05,-.75),(.2,-.65),(.05,-.45),(.25,-.4),(.1,-.25),(.2,-.1)])

def eagle(p,heads=1):
    p.ell(0,.05,.2,.32)
    for s in (-1,1):
        p.poly([(s*.12,-.25),(s*.55,-.7),(s*.95,-.75),(s*.85,-.5),(s*.98,-.42),(s*.82,-.25),(s*.95,-.15),(s*.75,.0),(s*.85,.1),(s*.4,.1),(s*.15,.15)])
        p.line([(s*.1,.3),(s*.32,.55),(s*.45,.55)],.08)
    p.poly([(-.08,.3),(.08,.3),(.3,.75),(.1,.65),(0,.82),(-.1,.65),(-.3,.75)])
    if heads==1:
        p.line([(0,-.2),(0,-.48)],.14); p.circ(0,-.55,.15); p.poly([(-.12,-.6),(-.32,-.5),(-.12,-.48)])
    else:
        for s in (-1,1):
            p.line([(0,-.2),(s*.22,-.5)],.13); p.circ(s*.25,-.58,.13); p.poly([(s*.35,-.62),(s*.52,-.52),(s*.35,-.5)])

def bird(p):  # standing bird, side view (jackdaw, falcon)
    p.ell(0,0,.45,.28); p.circ(-.42,-.32,.18); p.poly([(-.55,-.38),(-.82,-.28),(-.55,-.24)])
    p.poly([(.3,-.1),(.95,.15),(.85,.32),(.3,.2)]); p.line([(-.05,.25),(-.1,.7)],.07); p.line([(.12,.25),(.12,.7)],.07)

def fleur(p):
    p.poly([(0,-1),(.2,-.6),(.14,.02),(-.14,.02),(-.2,-.6)])
    for s in (-1,1):
        p.line([(s*.1,.05),(s*.45,-.05),(s*.62,-.38),(s*.5,-.58),(s*.36,-.45)],.15)
        p.line([(s*.08,.18),(s*.35,.45),(s*.5,.4)],.12)
    p.rect(-.36,.0,.36,.17); p.poly([(-.12,.17),(.12,.17),(0,.62)])

def castle(p):
    p.rect(-.7,-.1,.7,.8)
    for x in (-.7,-.15,.4):
        p.rect(x,-.6,x+.3,-.1)
        for i in range(3): p.rect(x+i*.12-.01,-.75,x+i*.12+.07,-.6)
    for i in range(5): p.rect(-.62+i*.28,-.22,-.5+i*.28,-.1)
    p.ell(0,.55,.15,.3,fill=0); p.rect(-.15,.55,.15,.8,fill=0)
    for x in (-.55,.0,.55): p.rect(x-.04,-.45,x+.04,-.25,fill=0)

def crescent(p,star=False):
    p.circ(0,0,.75); p.circ(.28,-.08,.62,fill=0)
    if star: star_(p,.55,-.05,.22,5)
def star_(p,x,y,r,n=5,inner=.45):
    pts=[]
    for i in range(2*n):
        a=-math.pi/2+i*math.pi/n; rr=r if i%2==0 else r*inner
        pts.append((x+rr*math.cos(a),y+rr*math.sin(a)))
    p.poly(pts)
def star(p,n=8,inner=.45): star_(p,0,0,1,n,inner)

def cross(p,w=.22,arm=1.0,kind='plain'):
    if kind=='formee':
        for a in range(4):
            r=lambda x,y,a=a:[(x,y),(-y,x),(-x,-y),(y,-x)][a]
            p.poly([r(0,0),r(-.42,-arm),r(.42,-arm)]); p.circ(0,0,.18)
        return
    p.rect(-w/2,-arm,w/2,arm); p.rect(-arm,-w/2,arm,w/2)
    if kind=='potent':
        for x,y in [(0,-arm),(0,arm)]: p.rect(-.35,y-w/2,.35,y+w/2)
        for x,y in [(-arm,0),(arm,0)]: p.rect(x-w/2,-.35,x+w/2,.35)
    if kind=='pommee':
        for x,y in [(0,-arm),(0,arm),(-arm,0),(arm,0)]: p.circ(x,y,w*.85)
    if kind=='toulouse':
        for x,y in [(0,-arm),(0,arm),(-arm,0),(arm,0)]:
            for o in (-.18,.18):
                p.circ(x+(o if x==0 else 0),y+(o if y==0 else 0),.1)
def double_cross(p):
    p.rect(-.09,-.9,.09,.9); p.rect(-.35,-.55,.35,-.4); p.rect(-.5,-.15,.5,.02)
def jerusalem(p):
    cross(p,.2,.85,'potent')
    for x,y in [(-.55,-.55),(.55,-.55),(-.55,.55),(.55,.55)]: p.rect(x-.05,y-.22,x+.05,y+.22); p.rect(x-.22,y-.05,x+.22,y+.05)
def byz_cross(p):
    cross(p,.16,.9)
    for x,y,f in [(-.5,-.5,1),(.5,-.5,-1),(-.5,.5,1),(.5,.5,-1)]:  # the four firesteels
        p.ring(x,y-.12,.17,.07); p.ring(x,y+.17,.17,.07)
        p.rect(x+(.12 if f>0 else -.19),y-.33,x+(.19 if f>0 else -.12),y+.38)
def keys(p):
    for s in (-1,1):
        q=Pen.__new__(Pen); q.__dict__.update(p.__dict__); a=math.radians(35*s)
        q.ca,q.sa=math.cos(a),math.sin(a)
        q.line([(0,-.55),(0,.8)],.1); q.ring(0,-.72,.2,.08)
        q.rect(0,.45,.28,.55); q.rect(0,.65,.28,.78)
def crowns3(p):
    for x,y in [(-.45,-.42),(.45,-.42),(0,.42)]: crown_(p,x,y,.36)
def crown_(p,x,y,r):
    p.rect(x-r,y,x+r,y+r*.45)
    for i in range(3):
        cx=x-r+r*i; p.poly([(cx-r*.25,y),(cx,y-r*.7),(cx+r*.25,y)] if i!=1 else [(cx-r*.3,y),(cx,y-r*.9),(cx+r*.3,y)]); p.circ(cx,y-r*(.75 if i!=1 else .95),r*.13)
    p.poly([(x-r,y),(x-r,y-r*.5),(x-r*.6,y)]); p.poly([(x+r,y),(x+r,y-r*.5),(x+r*.6,y)])
def harp(p):
    p.line([(-.45,-.75),(-.5,.8)],.14); p.line([(-.45,-.75),(.1,-.7),(.5,-.45),(.6,-.2)],.12)
    p.line([(-.5,.8),(.6,-.2)],.1)
    for i in range(1,5):
        t=i/5; x0=-.47; y0=-.73+1.5*t; p.line([(x0,y0),(x0+.6*t+.05,y0-.05)],.035)
def chains(p):
    p.line([(0,-1),(0,1)],.08); p.line([(-1,0),(1,0)],.08); p.line([(-.95,-.95),(.95,.95)],.08); p.line([(-.95,.95),(.95,-.95)],.08)
    p.line([(-.95,-.95),(.95,-.95),(.95,.95),(-.95,.95),(-.95,-.95)],.08)
def quinas(p):
    for x,y in [(0,-.55),(-.55,0),(0,0),(.55,0),(0,.55)]:
        p.poly([(x-.2,y-.24),(x+.2,y-.24),(x+.2,y+.06),(x,y+.25),(x-.2,y+.06)])
def checker(p):
    for i in range(4):
        for j in range(4):
            if (i+j)%2==0: p.rect(-.6+i*.3,-.6+j*.3,-.3+i*.3,-.3+j*.3)
def trident(p,prongs=3):
    p.line([(-.55,-.8),(-.6,.2),(-.25,.65),(0,.85),(.25,.65),(.6,.2),(.55,-.8)],.13)
    if prongs==3: p.line([(0,.85),(0,-.9)],.13); p.poly([(-.12,-.75),(0,-1),(.12,-.75)])
    p.line([(0,.85),(0,1)],.13)
    for x in (-.55,.55): p.poly([(x-.1,-.7),(x,-.95),(x+.1,-.7)])
def tamga(p,kind=0):
    if kind==0: p.ring(0,.25,.4,.12); p.line([(0,-.15),(0,-.9)],.12); p.line([(-.35,-.6),(.35,-.6)],.12)
    elif kind==1: p.line([(-.6,.7),(0,-.7),(.6,.7)],.13); p.line([(-.35,.15),(.35,.15)],.12)
    elif kind==3: p.line([(-.6,-.7),(-.5,-.1),(0,.15),(.5,-.1),(.6,-.7)],.13); p.line([(0,.15),(0,.9)],.13); p.line([(-.3,.6),(.3,.6)],.12)
    else: p.line([(0,.9),(0,-.3)],.13); p.line([(-.6,-.8),(0,-.3),(.6,-.8)],.13); p.circ(0,.9,.15)
def sun(p,rays=12):
    p.circ(0,0,.42)
    for i in range(rays):
        a=2*math.pi*i/rays; b=math.pi/rays*.55
        p.poly([(.5*math.cos(a-b),.5*math.sin(a-b)),(.95*math.cos(a),.95*math.sin(a)),(.5*math.cos(a+b),.5*math.sin(a+b))])
def wheel(p,spokes=8):
    p.ring(0,0,.85,.14); p.circ(0,0,.18)
    for i in range(spokes):
        a=2*math.pi*i/spokes; p.line([(0,0),(.75*math.cos(a),.75*math.sin(a))],.08)
def stupa(p):
    p.ell(0,.25,.55,.45); p.rect(-.75,.55,.75,.75); p.rect(-.15,-.45,.15,-.15); p.poly([(-.12,-.45),(0,-1),(.12,-.45)])
    p.rect(-.6,.25,.6,.6)
def towers(p):
    for x,h,w in [(-.7,.35,.18),(-.35,.6,.22),(0,.95,.28),(.35,.6,.22),(.7,.35,.18)]:
        p.poly([(x-w,.75),(x-w,.3-h*.2),(x-w*.6,-h*.5),(x,-h),(x+w*.6,-h*.5),(x+w,.3-h*.2),(x+w,.75)])
    p.rect(-.95,.6,.95,.8)
def palm(p):
    p.line([(.1,.9),(.05,.3),(-.05,-.35)],.12)
    for a in (-160,-125,-90,-55,-20,10,-190):
        r=math.radians(a); p.line([(-.05,-.38),(-.05+.45*math.cos(r),-.38+.3*math.sin(r)),(-.05+.75*math.cos(r),-.25+.45*math.sin(r)+.2)],.09)
def columns(p):
    p.rect(-.7,.2,.7,.38); p.rect(-.7,.2,-.45,.8); p.rect(.45,.2,.7,.8); p.rect(-.12,-.75,.12,.2)
    p.rect(-.45,-.45,-.2,.2); p.rect(.2,-.45,.45,.2); p.rect(-.45,-.45,.45,-.25)
def bow(p):
    p.line([(-.25,-.9),(.25,-.55),(.4,0),(.25,.55),(-.25,.9)],.11); p.line([(-.25,-.9),(-.25,.9)],.035)
    for y in (-.25,0,.25):
        p.line([(-.8,y),(.75,y)],.06); p.poly([(.7,y-.12),(.95,y),(.7,y+.12)])
def chakana(p):
    s=.27
    p.rect(-s,-3*s,s,3*s); p.rect(-3*s,-s,3*s,s); p.rect(-2*s,-2*s,2*s,2*s)
def wave(p):
    for y in (-.4,.0,.4):
        p.line([(-.95+.1*i,y+.12*math.sin(i*.9)) for i in range(20)],.1)
def mon(p):
    p.ring(0,0,.8,.12)
    for a in (0,120,240):
        r=math.radians(a-90); x,y=.32*math.cos(r),.32*math.sin(r); p.ell(x,y,.22,.22)
def axe(p): p.line([(0,-.9),(0,.9)],.1); p.poly([(.05,-.8),(.6,-.95),(.55,-.15),(.05,-.35)])
def lotus(p):
    for a in (-60,-30,0,30,60):
        q=Pen.__new__(Pen); q.__dict__.update(p.__dict__); r=math.radians(a); q.ca,q.sa=math.cos(r),math.sin(r)
        q.oy=p.t(0,.45)[1]; q.ox=p.t(0,.45)[0]; q.ell(0,-.55,.17,.5)
    p.rect(-.6,.45,.6,.6)
def ethiopian_cross(p):
    cross(p,.18,.85,'formee')
    for x,y in [(0,-.85),(0,.85),(-.85,0),(.85,0)]: p.ring(x,y,.18,.07)
def quarter_lions(c):
    for (x0,y0,x1,y1,bg,fg) in [(0,0,.5,.5,OR,GUL),(.5,0,1,.5,GUL,OR),(0,.5,.5,1,GUL,OR),(.5,.5,1,1,OR,GUL)]:
        c.rect(x0,y0,x1,y1,bg); c.charge(lion_passant,(x0+x1)/2,(y0+y1)/2,.42,fg,flip=False)

# ---- designs
def semee(c,fn,col,nx,ny,size,**kw):
    for j in range(ny):
        for i in range(nx+(j%2)):
            x=(i+(0.5 if j%2==0 else 0))/nx; y=(j+.5)/ny
            c.charge(fn,x,y,size,col,**kw)

D={
'JRS':lambda c:(c.field(ARG),c.charge(jerusalem,size=.85,col=OR,outline=None)),
'TRP':lambda c:(c.field(GUL),c.charge(cross,size=.8,col=OR,kind='toulouse',w=.24,arm=.75)),
'ANT':lambda c:(c.field(GUL),c.charge(cross,size=.85,col=OR,kind='formee')),
'AYB':lambda c:(c.field(OR),c.charge(eagle,size=.85,col=(150,30,25))),
'CIL':lambda c:(c.field(GUL),c.bordure(AZ,.16),c.charge(lion,size=.75,col=OR,crown=True)),
'RUM':lambda c:(c.field(TEAL),c.charge(eagle,size=.85,col=OR,heads=2)),
'ARQ':lambda c:(c.field(VERT),c.charge(crescent,size=.75,col=OR,star=True)),
'BYZ':lambda c:(c.field(PURP),c.charge(byz_cross,size=.9,col=OR)),
'CYK':lambda c:(c.field(GUL),c.charge(eagle,size=.85,col=OR,heads=2)),
'BLG':lambda c:(c.field(MAROON),[c.charge(lion,x,y,.38,OR) for x,y in [(.35,.3),(.65,.3),(.5,.72)]]),
'SRB':lambda c:(c.field(GUL),c.charge(eagle,size=.85,col=ARG,heads=2)),
'HNG':lambda c:(c.hstripes([GUL,ARG]*4,0,1),c.rect(.5,0,1,1,GUL),c.charge(double_cross,.75,.5,.85,ARG)),
'VNC':lambda c:(c.field(GUL),c.charge(lion_passant,size=.8,col=OR,wings=True)),
'HRE':lambda c:(c.field(OR),c.charge(eagle,size=.9,col=SAB,outline=None)),
'PSA':lambda c:(c.field(GUL),c.charge(cross,size=.8,col=ARG,kind='pommee',w=.2,arm=.72)),
'PPS':lambda c:(c.field(GUL),c.charge(keys,size=.8,col=OR)),
'SCL':lambda c:(c.field(AZ),[c.charge(lambda p,i=i,j=j:p.rect(-2.4+i*.3,-.3+j*.3,-2.1+i*.3,j*.3),.5,.5,.9,ARG if (i+j)%2 else GUL,ang=-30,outline=None) for i in range(16) for j in range(2)]),
'FRK':lambda c:(c.field(AZ),semee(c,fleur,OR,4,3,.26)),
'AGV':lambda c:(c.field(GUL),[c.charge(lion_passant,.5,y,.33,OR) for y in (.19,.5,.81)]),
'SCT':lambda c:(c.field(OR),c.charge(lion,size=.8,col=GUL)),
'GWY':quarter_lions,
'IRK':lambda c:(c.field(AZ),c.charge(harp,size=.8,col=OR)),
'CAS':lambda c:(c.field(GUL),c.charge(castle,size=.75,col=OR)),
'LEO':lambda c:(c.field(ARG),c.charge(lion,size=.8,col=PURP,crown=True)),
'NVR':lambda c:(c.field(GUL),c.charge(chains,size=.9,col=OR),c.charge(lambda p:p.circ(0,0,.14),size=.9,col=VERT)),
'ARN':lambda c:c.vstripes([OR,GUL]*4+[OR]),
'PRT':lambda c:(c.field(ARG),c.charge(quinas,size=.9,col=AZ)),
'ALM':lambda c:(c.field(GUL),c.rect(.5-.2*c.h/c.w,.3,.5+.2*c.h/c.w,.7,ARG),c.charge(checker,size=.68,col=SAB,outline=None)),
'MAJ':lambda c:(c.field(ARG),c.rect(0,0,.25,1,VERT),c.charge(crescent,.6,.5,.7,VERT,star=True)),
'DNK':lambda c:(c.field(GUL),c.rect(.31,0,.43,1,ARG),c.rect(0,.42,1,.58,ARG)),
'NRW':lambda c:(c.field(GUL),c.charge(lion,size=.8,col=OR,crown=True,axe=True)),
'SWD':lambda c:(c.field(AZ),c.charge(crowns3,size=.85,col=OR)),
'FNT':lambda c:(c.field(SKY),c.rect(0,.7,1,1,ARG),c.charge(sun,.5,.4,.55,ARG,outline=(40,70,110))),
'PRS':lambda c:(c.hstripes([ARG,SAB]),c.charge(sun,.5,.5,.6,OR)),
'LTH':lambda c:(c.field(GUL),c.charge(columns,size=.75,col=ARG)),
'LVN':lambda c:c.hstripes([MAROON,MAROON,ARG,MAROON,MAROON]),
'ESN':lambda c:(c.hstripes([AZ,SAB,ARG]),c.charge(star,.5,.17,.22,ARG,outline=None,n=8)),
'PLD':lambda c:(c.field(GUL),c.charge(eagle,size=.88,col=ARG)),
'NVG':lambda c:(c.field(GUL),c.charge(trident,size=.75,col=OR,prongs=2)),
'VSZ':lambda c:(c.field(AZ),c.charge(lion_passant,size=.7,col=OR)),
'SML':lambda c:(c.field(VERT),c.charge(trident,size=.75,col=OR,prongs=2)),
'PLT':lambda c:(c.field((40,50,110)),c.charge(trident,size=.75,col=ARG)),
'CRN':lambda c:(c.field((190,140,60)),c.charge(trident,size=.75,col=SAB,outline=None)),
'KYV':lambda c:(c.field(AZ),c.charge(trident,size=.78,col=OR)),
'VLH':lambda c:(c.field(GUL),c.charge(cross,size=.8,col=ARG,w=.26,arm=.75)),
'HLC':lambda c:(c.field(SKY),c.charge(bird,size=.75,col=SAB,outline=ARG)),
'CUM':lambda c:(c.field(SKY),c.charge(tamga,size=.75,col=OR,kind=3)),
'VBG':lambda c:(c.field(VERT),c.charge(crescent,size=.7,col=ARG)),
'KIP':lambda c:(c.field(TAN),c.charge(tamga,size=.75,col=SAB,kind=2,outline=None)),
'ALN':lambda c:(c.field(ARG),c.charge(cross,size=.8,col=GUL,kind='formee')),
'GRG':lambda c:(c.field(ARG),c.charge(cross,size=1,col=GUL,w=.26,arm=1.6,outline=None)),
'SHV':lambda c:(c.field((40,110,90)),c.charge(sun,size=.75,col=OR)),
'ABS':lambda c:(c.field(SAB),c.bordure(OR,.08),c.charge(crescent,size=.4,col=OR)),
'SLJ':lambda c:(c.field(GUL),c.charge(bow,size=.75,col=OR)),
'ILD':lambda c:(c.field((150,40,50)),c.charge(crescent,size=.7,col=ARG),[c.charge(star,x,y,.12,ARG,n=5) for x,y in [(.3,.25),(.7,.25),(.3,.75),(.7,.75)]]),
'SLG':lambda c:(c.field(PURP),c.charge(star,size=.75,col=OR,n=8)),
'KHW':lambda c:(c.field(TEAL),c.charge(crescent,size=.7,col=ARG,star=True)),
'GHR':lambda c:(c.field(OLIVE),c.charge(sun,size=.75,col=OR,rays=16)),
'UYN':lambda c:(c.field(GUL),c.rect(0,.85,1,1,VERT),c.charge(palm,size=.75,col=ARG)),
'NJD':lambda c:(c.field(VERT),c.rect(0,0,.22,1,ARG),c.charge(crescent,.6,.5,.65,ARG)),
'NAM':lambda c:(c.field(BRN),c.charge(sun,size=.7,col=TAN,rays=8)),
'MSA':lambda c:(c.field(TEAL),c.charge(sun,size=.75,col=OR,rays=16)),
'ADN':lambda c:(c.field(GUL),c.charge(chakana,size=.8,col=OR)),
'AMZ':lambda c:(c.field(VERT),c.charge(wave,size=.8,col=ARG,outline=None)),
'ICL':lambda c:(c.field(AZ),c.charge(bird,size=.75,col=ARG)),
'SAP':lambda c:(c.hstripes([AZ,GUL]),c.charge(lambda p:(p.ring(0,0,.75,.18)),size=.8,col=OR)),
'SBT':lambda c:(c.field(ARG),c.charge(sun,size=.7,col=SKY,outline=(40,70,110))),
'ABY':lambda c:(c.field(OR),c.charge(ethiopian_cross,size=.8,col=GUL)),
'MKR':lambda c:(c.field(ARG),c.charge(cross,size=.8,col=AZ,kind='formee')),
'GHN':lambda c:(c.field((200,140,40)),c.charge(star,size=.7,col=BRN,n=5)),
'BNT':lambda c:(c.hstripes([BRN,OR,BRN]),c.charge(lambda p:p.poly([(0,-.9),(.45,0),(0,.9),(-.45,0)]),size=.8,col=SAB)),
'HND':lambda c:(c.field(SAFF),c.charge(sun,size=.75,col=GUL,rays=16)),
'DCN':lambda c:(c.field(GUL),c.charge(lion,size=.8,col=OR)),
'TBT':lambda c:(c.field(MAROON),c.charge(wheel,size=.75,col=OR)),
'KRK':lambda c:(c.field((30,40,90)),c.charge(sun,.38,.5,.42,OR),c.charge(crescent,.66,.5,.42,ARG)),
'MGT':lambda c:(c.field(SKY),c.charge(lambda p:(p.poly([(-.2,-.45),(-.25,-.7),(-.1,-.62),(0,-.95),(.1,-.62),(.25,-.7),(.2,-.45)]),p.circ(0,-.15,.22),p.circ(0,.35,.3),p.circ(0,.22,.3,fill=0),p.rect(-.3,.7,.3,.8)),size=.85,col=OR)),
'XXA':lambda c:(c.field((150,60,40)),c.charge(lambda p:(p.rect(-.6,-.6,.6,.6),p.rect(-.45,-.45,.45,.45,fill=0),p.rect(-.3,-.3,.3,.3)),size=.8,col=ARG)),
'JIN':lambda c:(c.field(OR),c.charge(sun,size=.65,col=GUL,rays=12)),
'SOG':lambda c:(c.field(GUL),c.bordure(OR,.12),c.charge(lambda p:p.ring(0,0,.6,.15),size=.8,col=OR)),
'DAL':lambda c:(c.field(ARG),c.charge(lotus,size=.8,col=(170,40,100))),
'GRY':lambda c:(c.field(ARG),c.charge(lambda p:p.circ(0,0,.6),size=.8,col=GUL,outline=None),
                c.charge(lambda p:(p.poly([(-.6,0),(.6,0)]+[(.6*math.cos(math.radians(a)),.6*math.sin(math.radians(a))) for a in range(0,181,10)]),p.circ(-.3,0,.3),p.circ(.3,0,.3,fill=0)),size=.8,col=AZ,outline=None),
                c.charge(lambda p:p.circ(.3,0,.3),size=.8,col=GUL,outline=None)),
'JPN':lambda c:(c.field(ARG),c.charge(mon,size=.6,col=SAB,outline=None)),
'PGN':lambda c:(c.field(GUL),c.charge(stupa,size=.75,col=OR)),
'KHR':lambda c:(c.field(AZ),c.charge(towers,size=.75,col=ARG)),
'DVT':lambda c:(c.field(GUL),c.charge(lambda p:p.circ(0,0,.5),size=.8,col=OR),c.charge(star,size=.3,col=GUL,n=5,outline=None)),
'SRV':lambda c:(c.field(VERT),c.charge(lotus,size=.75,col=OR)),
'PHL':lambda c:(c.hstripes([AZ,GUL]),c.charge(sun,size=.6,col=OR,rays=8)),
'OCN':lambda c:(c.field(AZ),c.charge(wave,size=.75,col=ARG,outline=None)),
}

def draw_flag(tag,w=82,h=52,ss=8):
    c=Canvas(w,h,ss); D[tag](c)
    return c.img.resize((w,h),Image.LANCZOS)

def shield(tag,w=36,h=42):
    """The flag's design rendered as a heater shield, with a dark rim."""
    img=draw_flag(tag,w*4,h*4,2)
    m=Image.new('L',img.size,0); d=ImageDraw.Draw(m); W,H=img.size
    pts=[(0,0),(W,0),(W,H*.45)]+[(W/2+W/2*math.cos(math.radians(a)),H*.45+H*.55*math.sin(math.radians(a))) for a in range(0,91,6)]
    pts+=[(W/2-W/2*math.cos(math.radians(a)),H*.45+H*.55*math.sin(math.radians(a))) for a in range(90,-1,-6)]+[(0,H*.45)]
    d.polygon(pts,fill=255)
    rim=Image.new('RGBA',img.size,(40,25,15,255)); out=Image.new('RGBA',img.size,(0,0,0,0))
    out.paste(rim,(0,0),m); inner=m.filter(ImageFilter.MinFilter(9)); out.paste(img,(0,0),inner)
    return out.resize((w,h),Image.LANCZOS)
