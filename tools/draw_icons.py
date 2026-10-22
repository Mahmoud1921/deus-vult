import math,sys
from PIL import Image,ImageDraw,ImageFilter,ImageChops
V="/mnt/user-data/uploads/Hearts of Iron IV/gfx/interface/"
K=8
def canvas(w,h): 
    m=Image.new('L',(w*K,h*K),0); return m,ImageDraw.Draw(m)
def line(d,pts,wid,fill=255):
    pts=[(x*K,y*K) for x,y in pts]; d.line(pts,fill=fill,width=int(wid*K),joint='curve')
    for x,y in (pts[0],pts[-1]): r=wid*K/2; d.ellipse([x-r,y-r,x+r,y+r],fill=fill)
def poly(d,pts,fill=255): d.polygon([(x*K,y*K) for x,y in pts],fill=fill)
def ell(d,b,fill=255): d.ellipse([b[0]*K,b[1]*K,b[2]*K,b[3]*K],fill=fill)
def finish(mask,w,h,top,bot,shadow=True):
    m=mask.resize((w,h),Image.LANCZOS)
    grad=Image.new('RGBA',(w,h))
    for y in range(h):
        t=y/max(1,h-1); c=tuple(int(top[i]*(1-t)+bot[i]*t) for i in range(3))
        ImageDraw.Draw(grad).line([(0,y),(w,y)],fill=c+(255,))
    # edge darkening
    er=m.filter(ImageFilter.MinFilter(3))
    edge=ImageChops.subtract(m,er)
    dark=Image.new('RGBA',(w,h),(25,40,25,255))
    body=Image.composite(dark,grad,edge.point(lambda v:int(v*0.7)))
    body.putalpha(m)
    out=Image.new('RGBA',(w,h),(0,0,0,0))
    if shadow:
        sh=Image.new('RGBA',(w,h),(0,0,0,0)); sm=m.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v:int(v*0.6))
        sh.putalpha(sm); out.alpha_composite(sh,(1,1))
    out.alpha_composite(body); return out
GREEN=((125,165,110),(55,95,55)); WHITE=((250,250,250),(190,190,190)); BROWN=((215,170,125),(150,105,70))
def helm(w,h,cx,cy,s):
    m,d=canvas(w,h)
    # conical nasal helm, front view
    poly(d,[(cx-9*s,cy+3*s),(cx-8*s,cy-4*s),(cx-4*s,cy-10*s),(cx,cy-13*s),(cx+4*s,cy-10*s),(cx+8*s,cy-4*s),(cx+9*s,cy+3*s)])
    poly(d,[(cx-10*s,cy+1*s),(cx+10*s,cy+1*s),(cx+10*s,cy+4.5*s),(cx-10*s,cy+4.5*s)])  # brow band
    poly(d,[(cx-1.6*s,cy+4*s),(cx+1.6*s,cy+4*s),(cx+1.2*s,cy+12*s),(cx-1.2*s,cy+12*s)])  # nasal
    poly(d,[(cx-10*s,cy+4*s),(cx+10*s,cy+4*s),(cx+9*s,cy+12*s),(cx+5*s,cy+14*s),(cx-5*s,cy+14*s),(cx-9*s,cy+12*s)])
    poly(d,[(cx-7.5*s,cy+5.5*s),(cx-2.6*s,cy+5.5*s),(cx-2.6*s,cy+8*s),(cx-7*s,cy+8*s)],fill=0)
    poly(d,[(cx+7.5*s,cy+5.5*s),(cx+2.6*s,cy+5.5*s),(cx+2.6*s,cy+8*s),(cx+7*s,cy+8*s)],fill=0)
    return m
def knight(w,h):
    # base: vanilla horse frame, add rider with lance and shield
    m,d=canvas(w,h)
    # rider torso sitting on the horse's back (~x 30-38, y 12-18 in 76x42 space)
    poly(d,[(30,15),(37,15),(36,6),(31,6)])
    ell(d,(30.5,1.5,36.5,7.5))            # helmeted head
    poly(d,[(30.5,4.5),(36.5,4.5),(36.5,7.5),(30.5,7.5)])  # flat-top great helm
    line(d,[(26,13),(60,3)],2.2)          # couched lance
    poly(d,[(55,2),(64,0.5),(58,6)])      # pennant
    poly(d,[(25.5,8),(33,8),(33,15.5),(29.2,20.5),(25.5,15.5)])  # kite shield
    return m
def trebuchet(w,h,ox=0,oy=0,s=1.0):
    m,d=canvas(w,h)
    X=lambda x:ox+x*s; Y=lambda y:oy+y*s
    line(d,[(X(4),Y(38)),(X(48),Y(38))],4.3)        # base beam
    line(d,[(X(14),Y(38)),(X(26),Y(16))],3.5)     # A-frame
    line(d,[(X(38),Y(38)),(X(26),Y(16))],3.5)
    line(d,[(X(18),Y(31)),(X(34),Y(31))],2.3)
    line(d,[(X(36),Y(24)),(X(10),Y(4))],3.2)       # throwing arm (raised)
    poly(d,[(X(33),Y(22)),(X(43),Y(22)),(X(43),Y(31)),(X(33),Y(31))])  # counterweight
    line(d,[(X(10),Y(4)),(X(6),Y(13))],1.4)        # sling
    ell(d,(X(3.5),Y(11.5),X(9),Y(17)))            # stone
    ell(d,(X(5),Y(35),X(11),Y(41))); ell(d,(X(41),Y(35),X(47),Y(41)))  # wheels
    return m
def bow(w,h,ox=0,oy=0,s=1.0):
    m,d=canvas(w,h)
    X=lambda x:ox+x*s; Y=lambda y:oy+y*s
    pts=[(X(24+16*math.cos(t)),Y(20+17*math.sin(t))) for t in [math.radians(a) for a in range(-80,81,8)]]
    line(d,pts,4.0)                                  # bow limb
    line(d,[pts[0],pts[-1]],1.2)                     # string
    line(d,[(X(6),Y(20)),(X(44),Y(20))],1.9)        # arrow shaft
    poly(d,[(X(44),Y(17)),(X(50),Y(20)),(X(44),Y(23))])  # head
    poly(d,[(X(6),Y(20)),(X(2),Y(16.5)),(X(8),Y(20)),(X(2),Y(23.5))])  # fletching
    return m
def sword_shield(w,h):
    m,d=canvas(w,h)
    poly(d,[(14,9.5),(52,9.5),(57,11.5),(52,13.5),(14,13.5)])   # blade
    line(d,[(14,5),(14,18)],2.6)          # crossguard
    line(d,[(5,11.5),(13,11.5)],3.0)      # grip
    ell(d,(1,8.5,7,14.5))                 # pommel
    poly(d,[(55,1),(75,1),(75,12),(65,22),(55,12)])  # kite shield
    poly(d,[(64,3),(66,3),(66,18),(64,18)],fill=0)
    poly(d,[(57.5,7),(72.5,7),(72.5,9),(57.5,9)],fill=0)
    return m
def sheet(frame1,orig):
    o=Image.open(orig).convert('RGBA'); w=o.width//2
    o.paste(Image.new('RGBA',(w,o.height),(0,0,0,0)),(0,0)); o.alpha_composite(frame1,(0,0)); return o
out={}
out['counters/divisions_large/unit_infantry_icon.dds']=sheet(finish(helm(76,42,38,20,1.25),76,42,*GREEN),V+'counters/divisions_large/unit_infantry_icon.dds')
hf=Image.open(V+'counters/divisions_large/unit_cavalry_icon.dds').convert('RGBA').crop((0,0,76,42)); hf.alpha_composite(finish(knight(76,42),76,42,*GREEN))
out['counters/divisions_large/unit_cavalry_icon.dds']=sheet(hf,V+'counters/divisions_large/unit_cavalry_icon.dds')
out['counters/divisions_large/unit_art_icon.dds']=sheet(finish(trebuchet(76,42,12,0,1.0),76,42,*GREEN),V+'counters/divisions_large/unit_art_icon.dds')
out['counters/divisions_large/unit_dv_archers_icon.dds']=sheet(finish(bow(76,42,12,1,1.0),76,42,*GREEN),V+'counters/divisions_large/unit_infantry_icon.dds')
out['counters/divisions_small/onmap_unit_infantry_icon.dds']=sheet(finish(helm(30,12,15,6,0.42),30,12,*WHITE,shadow=False),V+'counters/divisions_small/onmap_unit_infantry_icon.dds')
out['archetypes/archetype_infantry_equipment.dds']=finish(sword_shield(81,23),81,23,*BROWN)
out['archetypes/archetype_artillery_equipment.dds']=finish(trebuchet(74,36,10,-2,0.9),74,36,*BROWN)
import os
D=sys.argv[1]
for k,im in out.items():
    p=os.path.join(D,'gfx/interface',k); os.makedirs(os.path.dirname(p),exist_ok=True); im.save(p.replace('.dds','.png'))
# preview
ims=[im.resize((im.width*4,im.height*4),Image.NEAREST) for im in out.values()]
W=max(i.width for i in ims); H=sum(i.height+10 for i in ims)
pv=Image.new('RGBA',(W,H),(90,90,90,255)); y=0
for i in ims: pv.alpha_composite(i,(0,y)); y+=i.height+10
pv.save(os.path.join(D,'preview.png'))
