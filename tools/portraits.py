# Leader portraits in the style of a painted icon: gold ground under an arch, flat colours
# with dark outlines, the realm's arms on a small shield. draw_portrait(tag) returns 156x210 RGBA.
import math,random
from PIL import Image, ImageDraw, ImageFilter
from heraldry import shield, draw_flag

W,H,S=156,210,4
INK=(45,28,18)
SKIN={'l':(238,200,168),'m':(214,166,124),'o':(192,146,104),'d':(146,98,64),'e':(236,203,160)}
HAIR={'blk':(38,30,26),'brn':(96,60,34),'red':(150,72,34),'bld':(196,156,88),'gry':(150,144,138),'wht':(226,222,214)}
GOLD=(226,180,64); WHITE=(242,238,228); BLACK=(32,30,32)

# tag: headwear, hair, beard, skin [, extra options]
LOOK={
'JRS':('crown','bld','short','l'),'TRP':('circlet','brn','full','m'),'ANT':('circlet','bld','short','l'),
'AYB':('turban','blk','full','m',{'turban':WHITE,'kulah':(200,160,40)}),'CIL':('crown','blk','full','m'),
'RUM':('turban','gry','long','m',{'kulah':(170,40,40)}),'ARQ':('turban','blk','full','m',{'turban':(210,200,170)}),
'BYZ':('kamelaukion','brn','full','l'),'CYK':('kamelaukion','blk','pointed','m'),'BLG':('kamelaukion','blk','full','l'),
'SRB':('crown','wht','long','l'),'HNG':('kamelaukion','brn','full','l'),'VNC':('doge','wht','full','l'),
'HRE':('imperial','red','full','l'),'PSA':('mitre','gry','none','l',{'robe':(200,160,60)}),'PPS':('tiara','wht','none','l',{'robe':(170,25,30)}),
'SCL':('crown','blk','short','l'),'FRK':('crown','brn','none','l'),'AGV':('crown','red','short','l'),'SCT':('crown','red','full','l'),
'GWY':('circlet','brn','full','l'),'IRK':('circlet','red','moustache','l'),'CAS':('crown','bld','short','l'),'LEO':('crown','gry','full','l'),
'NVR':('crown','gry','full','l'),'ARN':('crown','brn','none','l'),'PRT':('crown','brn','full','l'),
'ALM':('turban','blk','full','m'),'MAJ':('litham','blk','none','m'),'DNK':('crown','bld','short','l'),'NRW':('crown','red','full','l'),
'SWD':('crown','bld','full','l'),'FNT':('none','wht','long','l'),'PRS':('helmet','bld','full','l'),'LTH':('helmet','brn','full','l'),
'LVN':('none','gry','long','l'),'ESN':('helmet','bld','full','l'),'PLD':('crown','brn','full','l'),'NVG':('furcap','brn','full','l'),
'VSZ':('furcap','brn','long','l'),'SML':('furcap','gry','full','l'),'PLT':('furcap','bld','full','l'),'CRN':('furcap','brn','pointed','l'),
'KYV':('furcap','gry','long','l'),'VLH':('furcap','blk','short','l'),'HLC':('furcap','wht','long','l'),
'CUM':('steppe','blk','moustache','m'),'VBG':('turban','brn','full','l'),'KIP':('steppe','blk','pointed','m'),'ALN':('helmet','blk','full','m'),
'GRG':('veil','blk','none','l',{'female':True}),'SHV':('turban','blk','full','m'),'ABS':('turban','blk','full','m',{'turban':BLACK}),
'SLJ':('turban','blk','pointed','m',{'kulah':(40,90,160)}),'ILD':('turban','brn','full','m'),'SLG':('turban','blk','short','m'),
'KHW':('steppe','blk','full','m'),'GHR':('turban','blk','full','o'),'UYN':('turban','blk','full','o',{'turban':(240,240,230)}),
'NJD':('turban','blk','full','o',{'turban':(230,230,220)}),
'NAM':('feather','blk','none','d'),'MSA':('feather','blk','none','d'),'ADN':('feather','blk','none','d'),'AMZ':('feather','blk','none','d'),
'ICL':('none','bld','full','l'),'SAP':('steppe','brn','short','l'),'SBT':('steppe','blk','none','e'),
'ABY':('ethiopian','blk','short','d'),'MKR':('crown','blk','short','d'),'GHN':('turban','blk','short','d',{'turban':(240,236,226)}),
'BNT':('feather','blk','none','d'),'HND':('rajput','blk','moustache','o'),'DCN':('mukuta','blk','moustache','o'),
'TBT':('steppe','blk','none','e'),'KRK':('steppe','blk','moustache','e'),'MGT':('steppe','blk','moustache','e'),
'XXA':('futou','blk','moustache','e'),'JIN':('futou','blk','pointed','e'),'SOG':('futou','blk','pointed','e'),'DAL':('futou','blk','moustache','e'),
'GRY':('futou','blk','pointed','e'),'JPN':('eboshi','blk','moustache','e'),'PGN':('mukuta','blk','none','o'),'KHR':('mukuta','blk','none','o'),
'DVT':('futou','blk','none','e'),'SRV':('mukuta','blk','none','o'),'PHL':('feather','blk','none','o'),'OCN':('feather','blk','none','o'),
}

def dark(c,f=.6): return tuple(int(v*f) for v in c[:3])
def light(c,f=.35): return tuple(int(v+(255-v)*f) for v in c[:3])

class P:
    def __init__(s):
        s.img=Image.new('RGBA',(W*S,H*S),(0,0,0,255))
    def m(s): m=Image.new('L',s.img.size,0); return m,ImageDraw.Draw(m)
    def put(s,m,col,ol=INK,ow=2.0):
        if ol: s.img.paste(ol+(255,),(0,0),m.filter(ImageFilter.MaxFilter(int(ow*S)|1)))
        s.img.paste(col+(255,),(0,0),m)
    def poly(s,pts,col,ol=INK,ow=2.0):
        m,d=s.m(); d.polygon([(x*S,y*S) for x,y in pts],fill=255); s.put(m,col,ol,ow)
    def ell(s,x0,y0,x1,y1,col,ol=INK,ow=2.0):
        m,d=s.m(); d.ellipse([x0*S,y0*S,x1*S,y1*S],fill=255); s.put(m,col,ol,ow)
    def line(s,pts,col,w,ol=None):
        d=ImageDraw.Draw(s.img)
        if ol: d.line([(x*S,y*S) for x,y in pts],fill=ol+(255,),width=int((w+1.6)*S),joint='curve')
        d.line([(x*S,y*S) for x,y in pts],fill=col+(255,),width=int(w*S),joint='curve')
    def dot(s,x,y,r,col):
        ImageDraw.Draw(s.img).ellipse([(x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S],fill=col+(255,))

def arc(cx,cy,rx,ry,a0,a1,n=24):
    return [(cx+rx*math.cos(math.radians(a0+(a1-a0)*i/n)),cy+ry*math.sin(math.radians(a0+(a1-a0)*i/n))) for i in range(n+1)]

def palette(tag):
    f=draw_flag(tag,41,26).convert('RGB'); cols=sorted(f.getcolors(4096),reverse=True)
    main=cols[0][1]
    second=next((c for n,c in cols[1:] if sum(abs(a-b) for a,b in zip(c,main))>120),dark(main))
    return main,second

def background(p,main,second):
    p.img.paste(dark(main,.45)+(255,),(0,0,W*S,H*S))
    m,d=p.m(); d.rectangle([8*S,70*S,148*S,203*S],fill=255); d.ellipse([8*S,8*S,148*S,132*S],fill=255)
    g=Image.new('RGBA',p.img.size)
    gd=ImageDraw.Draw(g)
    for y in range(H*S):
        t=y/(H*S); gd.line([(0,y),(W*S,y)],fill=(int(236-30*t),int(196-40*t),int(104-40*t),255))
    rnd=random.Random(7)
    for _ in range(900):   # gold leaf texture
        x,y=rnd.randrange(W*S),rnd.randrange(H*S); r=rnd.randrange(2,7); v=rnd.choice([(250,220,140,255),(190,140,50,255)])
        gd.ellipse([x-r,y-r,x+r,y+r],fill=v)
    g=g.filter(ImageFilter.GaussianBlur(2))
    p.img.paste(INK+(255,),(0,0),m.filter(ImageFilter.MaxFilter(13)))
    p.img.paste(g,(0,0),m)
    # punched border dots along the arch
    for x,y in arc(78,70,66,58,180,360,30): p.dot(x,y,1.2,(160,110,40))

def draw_portrait(tag):
    hat,hair,beard,skin,*opt=LOOK[tag]; o=opt[0] if opt else {}
    sk=SKIN[skin]; hc=HAIR[hair]; fem=o.get('female')
    main,second=palette(tag); robe=o.get('robe',main)
    p=P(); background(p,main,second)
    # hair or veil behind the head
    if hat=='veil': p.poly(arc(78,92,34,40,180,360)+[(118,150),(122,175),(34,175),(38,150)],WHITE)
    elif hair in ('wht','gry') and beard=='long' or hat=='none' and beard=='long': p.ell(50,62,106,128,hc)
    elif hat in ('none','circlet','crown','imperial','helmet','furcap'): p.ell(52,62,104,118,hc)
    # body
    p.poly([(4,211),(14,176),(36,156),(62,146),(94,146),(120,156),(142,176),(152,211)],dark(second,.85) if robe==main else robe)
    p.poly([(30,211),(40,168),(62,150),(94,150),(116,168),(126,211)],robe if robe!=main else main)
    p.line([(40,168),(30,211)],GOLD,2.5); p.line([(116,168),(126,211)],GOLD,2.5)
    # neck
    p.poly([(67,112),(89,112),(91,152),(65,152)],dark(sk,.88))
    p.poly(arc(78,150,26,10,0,180),GOLD)
    for x,y in arc(78,152,24,8,10,170,8): p.dot(x,y,1.6,(170,30,40))
    p.ell(104,160,116,172,GOLD); p.dot(110,166,2.4,(160,25,40))
    if tag=='PSA': p.poly([(74,150),(82,150),(84,211),(72,211)],WHITE)  # pallium
    # ears and head
    p.ell(51,88,59,104,sk); p.ell(97,88,105,104,sk)
    p.ell(55,64,101,124,sk)
    p.ell(60,102,70,110,light((220,120,110),.6),None); p.ell(86,102,96,110,light((220,120,110),.6),None)
    # hair on top
    if hat in ('none','circlet','crown','imperial') and not fem:
        p.poly(arc(78,86,25,26,190,350)+[(100,80),(94,72),(78,70),(62,72),(56,80)],hc,ow=1.5)
    # face
    for ex in (69,87):
        p.ell(ex-5,89.5,ex+5,95,WHITE,INK,1.2); p.dot(ex,92.3,2.3,(70,45,30)); p.dot(ex,92.3,1,(10,10,10))
        p.line([(ex-6,89),(ex,87.5),(ex+6,89)],INK,1)
    bc=dark(hc,.8) if hair not in ('wht','gry') else dark(hc,.7)
    p.line([(62,85),(68,83),(74,84.5)],bc,1.8); p.line([(82,84.5),(88,83),(94,85)],bc,1.8)
    p.line([(79,90),(76,104),(78,107),(82,106)],dark(sk,.65),1.3)
    if hair in ('gry','wht'):   # age lines
        for ex,f in ((69,-1),(87,1)): p.line([(ex+f*7,94),(ex+f*9,96)],dark(sk,.7),.8); p.line([(ex+f*7,91),(ex+f*9.5,92)],dark(sk,.7),.8)
        p.line([(68,76),(88,76)],dark(sk,.78),.8); p.line([(70,79.5),(86,79.5)],dark(sk,.78),.8)
    lip=(150,60,55) if not fem else (175,60,70)
    p.line([(71,115),(78,116),(85,115)],lip,1.8)
    # beard
    if beard in ('short','full','long','pointed'):
        chin={'short':127,'full':136,'long':156,'pointed':142}[beard]
        out=[(55,92),(56,106),(62,118),(70,chin-4),(78,chin),(86,chin-4),(94,118),(100,106),(101,92)]
        if beard=='pointed': out=[(55,92),(57,108),(66,122),(78,chin),(90,122),(99,108),(101,92)]
        inner=[(97,94),(95,108),(88,112),(78,110),(68,112),(61,108),(59,94)]
        p.poly(out+inner,hc,ow=1.5)
        p.poly([(68,110),(78,108),(88,110),(90,114),(78,112),(66,114)],hc,ow=1)
        p.line([(72,116),(78,117),(84,116)],lip,1.6)
    elif beard=='moustache':
        p.poly([(64,116),(70,110),(78,109),(86,110),(92,116),(84,113),(78,112),(72,113)],hc,ow=1)
    # headwear
    hcol=o.get('turban',(235,232,220))
    if hat=='crown' or hat=='imperial' or (hat=='veil'):
        p.poly([(54,76),(56,62),(62,68),(67,54),(73,66),(78,50),(83,66),(89,54),(94,68),(100,62),(102,76)],GOLD)
        for x in (60,70,78,86,96): p.dot(x,72,1.8,(170,30,40) if x!=78 else (40,80,170))
        for x,y in ((67,53),(78,49),(89,53)): p.dot(x,y,2,GOLD)
        if hat=='imperial':
            p.line([(78,46),(78,33)],GOLD,3,INK); p.line([(72,38),(84,38)],GOLD,3,INK); p.line([(58,64),(66,52),(78,46),(90,52),(98,64)],GOLD,3,INK)
    elif hat=='circlet':
        p.poly([(55,72),(101,72),(101,78),(55,78)],GOLD,ow=1.5)
        for x in (63,78,93): p.dot(x,75,1.6,(170,30,40))
    elif hat=='kamelaukion':
        p.poly(arc(78,76,25,30,180,360),GOLD)
        for a in range(195,350,20):
            x,y=78+22*math.cos(math.radians(a)),76+18*math.sin(math.radians(a)); p.dot(x,y,1.5,WHITE)
        p.poly([(53,72),(103,72),(103,80),(53,80)],GOLD,ow=1.5)
        for x in range(57,102,6): p.dot(x,76,1.4,(170,30,40) if x%12 else (40,80,170))
        for x in (55,101):
            p.line([(x,80),(x-1,110)],GOLD,1.5)
            for y in range(84,112,6): p.dot(x-1+(y-84)/30,y,1.8,WHITE)
        p.line([(78,46),(78,38)],GOLD,2.5); p.line([(74,41),(82,41)],GOLD,2.5)
    elif hat in ('turban','litham'):
        if 'kulah' in o: p.poly(arc(78,62,13,20,180,360),o['kulah'])
        p.ell(46,52,110,84,hcol)
        for i,y in enumerate((60,67,74)): p.line(arc(78,y+8,30-i*2,12,200,340,16),dark(hcol,.78),1.4)
        p.dot(78,62,3,(170,30,40)); p.dot(78,62,1.4,GOLD)
        if hat=='litham': p.poly([(54,98),(102,98),(104,122),(94,140),(62,140),(52,122)],(40,50,90))
    elif hat=='tiara':
        p.poly([(58,78),(66,48),(78,26),(90,48),(98,78)],WHITE); p.poly([(58,68),(98,68),(98,78),(58,78)],GOLD,ow=1.5); p.dot(78,25,3,GOLD)
    elif hat=='mitre':
        p.poly([(58,78),(60,52),(78,34),(96,52),(98,78)],WHITE); p.poly([(75,40),(81,40),(81,78),(75,78)],GOLD,ow=1)
        p.poly([(58,70),(98,70),(98,78),(58,78)],GOLD,ow=1.5)
    elif hat=='doge':
        p.poly([(55,78),(57,58),(66,48),(84,44),(96,40),(102,54),(101,78)],(200,160,60)); p.poly([(55,72),(101,72),(101,78),(55,78)],WHITE,ow=1.5)
        for x,y in ((66,62),(80,56),(92,60),(74,52)): p.dot(x,y,1.5,(170,40,40))
    elif hat=='furcap':
        p.poly(arc(78,74,22,26,180,360),main if main!=(244,242,234) else (170,40,40))
        p.ell(52,66,104,82,(110,75,45),INK,1.5)
        for x in range(56,102,5): p.dot(x,72+(x%3),1.4,(80,52,30))
        p.line([(78,48),(78,40)],GOLD,2.5); p.line([(74,43),(82,43)],GOLD,2.5)
    elif hat=='steppe':
        p.poly([(52,78),(62,52),(78,34),(94,52),(104,78)],dark(second,.9) if second!=(244,242,234) else (160,50,40))
        p.ell(50,68,106,84,(120,85,50),INK,1.5); p.dot(78,34,3,GOLD)
    elif hat=='helmet':
        p.poly([(53,82),(60,58),(78,36),(96,58),(103,82)],(150,155,160)); p.line([(66,58),(78,40)],(205,210,215),2)
        p.poly([(53,76),(103,76),(103,83),(53,83)],(110,112,118),ow=1.5); p.poly([(76,82),(80,82),(80,104),(76,104)],(140,145,150),ow=1)
    elif hat=='futou':
        p.poly([(10,64),(146,64),(146,68),(10,68)],BLACK,ow=1)
        p.poly(arc(78,76,25,22,180,360),BLACK); p.poly(arc(78,58,14,14,180,360),BLACK)
    elif hat=='eboshi':
        p.poly([(56,78),(58,52),(70,30),(86,22),(96,30),(100,78)],BLACK)
    elif hat=='rajput':
        p.ell(48,52,108,84,(200,60,50))
        for i,y in enumerate((60,68,75)): p.line(arc(78,y+8,30-i*2,12,200,340,16),(240,170,50),1.6)
        p.dot(78,62,3.4,WHITE); p.dot(78,62,1.8,(40,120,80)); p.line([(80,58),(92,40),(96,30)],(240,230,210),2.5)
        p.dot(52,110,2.4,GOLD); p.dot(104,110,2.4,GOLD)
    elif hat=='mukuta':
        for y0,y1,hw in ((80,66,26),(68,54,20),(56,42,13)): p.poly([(78-hw,y0),(78+hw,y0),(78+hw-4,y1),(78-hw+4,y1)],GOLD,ow=1.5)
        p.poly([(71,44),(85,44),(78,18)],GOLD,ow=1.5)
        for x in (60,78,96): p.dot(x,74,1.8,(170,30,40))
        p.dot(52,112,2.4,GOLD); p.dot(104,112,2.4,GOLD)
    elif hat=='ethiopian':
        p.poly([(56,78),(58,52),(98,52),(100,78)],GOLD)
        for y in (58,66,72):
            for x in range(62,96,8): p.dot(x,y,1.5,(170,30,40) if y==66 else (40,90,60))
        p.line([(78,52),(78,36)],GOLD,3); p.line([(71,42),(85,42)],GOLD,3)
    elif hat=='feather':
        for a in (-50,-25,0,25,50):
            r=math.radians(a-90); x,y=78+40*math.cos(r),70+40*math.sin(r)
            p.poly([(78+5*math.cos(r+1.6),70+5*math.sin(r+1.6)),(x,y),(78+5*math.cos(r-1.6),70+5*math.sin(r-1.6))],(230,230,220) if a%50 else (180,60,40),ow=1)
        p.poly(arc(78,86,25,26,190,350)+[(100,80),(78,72),(56,80)],hc,ow=1.5)
        p.poly([(54,72),(102,72),(102,79),(54,79)],(180,60,40),ow=1.5)
        for x in range(58,100,8): p.dot(x,75.5,1.6,WHITE)
    # arms
    sh=shield(tag,34,40).resize((34*S,40*S),Image.LANCZOS)
    p.img.alpha_composite(sh,(114*S,164*S))
    return p.img.resize((W,H),Image.LANCZOS)
