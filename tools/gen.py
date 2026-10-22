import json,re,os,glob,shutil
from nations import N,GFX
from PIL import Image,ImageDraw
A={int(k):v for k,v in json.load(open('assign.json')).items()}
ARMY=json.load(open('army_summary.json')) if os.path.exists('army_summary.json') else {}
OUT='out'; shutil.rmtree(OUT,ignore_errors=True)
def w(p,s,bom=False):
    p=os.path.join(OUT,p); os.makedirs(os.path.dirname(p),exist_ok=True)
    open(p,'w',encoding='utf-8-sig' if bom else 'utf-8',newline='\n').write(s)
rows={int(l.split('\t')[0]):l.rstrip('\n').split('\t') for l in open('s.tsv')}
CLAIMS={454:['AYB'],455:['AYB'],553:['AYB'],799:['AYB'],183:['BYZ'],345:['BYZ'],15:['FRK'],14:['FRK'],30:['FRK'],23:['FRK'],19:['FRK'],25:['FRK'],806:['FRK'],48:['BLG'],212:['BLG'],163:['VNC']}
# --- states
manp={}
def strip_blocks(t,pat):
    while True:
        m=re.search(pat,t)
        if not m: return t
        i=m.end(); d=1
        while d: 
            d+= {'{':1,'}':-1}.get(t[i],0); i+=1
        t=t[:m.start()]+t[i:]
for f in glob.glob('v/history/states/*.txt'):
    t=open(f,encoding='utf-8-sig',errors='replace').read()
    sid=int(re.search(r'\bid\s*=\s*(\d+)',t).group(1))
    manp[sid]=int(re.search(r'manpower\s*=\s*(\d+)',t).group(1))
    hs=re.search(r'history\s*=\s*\{',t)
    i=hs.end(); d=1
    while d:
        d+={'{':1,'}':-1}.get(t[i],0); i+=1
    h=t[hs.end():i-1]
    h=strip_blocks(h,r'\b\d{3,4}\.\d{1,2}\.\d{1,2}(?:\.\d+)?\s*=\s*\{')
    h=re.sub(r'^[ \t]*(owner|controller|add_core_of|add_claim_by|set_demilitarized_zone)\s*=\s*[\w"]+[^\n]*\n','',h,flags=re.M)
    h=re.sub(r'\b(owner|controller|add_core_of|add_claim_by)\s*=\s*\w+','',h)
    tag=A[sid]
    ins=f"\n\t\towner = {tag}\n\t\tadd_core_of = {tag}\n"+''.join(f"\t\tadd_claim_by = {c}\n" for c in CLAIMS.get(sid,[]))
    t=t[:hs.end()]+ins+h+t[i-1:]
    w('history/states/'+os.path.basename(f),t)
# --- countries
tags=[];loc=['l_english:']
owned={}
for s,tg in A.items(): owned.setdefault(tg,[]).append(s)
for tag,(name,adj,g,col,cap,rel,leader,_) in N.items():
    if tag not in owned: print('no states',tag); continue
    if cap is None or A.get(cap)!=tag: cap=max(owned[tag],key=lambda s:manp[s])
    fn=re.sub(r'[^A-Za-z ]','',name)
    tags.append(f'{tag} = "countries/{fn}.txt"')
    gc=GFX[g]
    w(f'common/countries/{fn}.txt',f'graphical_culture = {gc}_gfx\ngraphical_culture_2d = {gc}_2d\n\ncolor = {{ {col[0]} {col[1]} {col[2]} }}\n')
    L=f'''\ncreate_country_leader = {{
	name = "{leader}"
	desc = ""
	expire = "1300.1.1.1"
	ideology = despotism
	traits = {{ }}
}}\n''' if leader else ''
    oob=f'oob = "{tag}_1187"\n' if tag in ARMY else ''
    art='\tgw_artillery = 1\n' if ARMY.get(tag,['warband'])[0] in ('feudal','askar') else ''
    w(f'history/countries/{tag} - {fn}.txt',f'''capital = {cap}
{oob}
set_research_slots = 2
set_stability = 0.6
set_war_support = 0.5
add_ideas = dv_{rel}

set_technology = {{
	infantry_weapons = 1
{art}}}

set_politics = {{
	ruling_party = neutrality
	last_election = "1180.1.1"
	election_frequency = 48
	elections_allowed = no
}}
set_popularities = {{
	democratic = 0
	fascism = 0
	communism = 0
	neutrality = 100
}}
{L}''')
    the = '' if name.endswith(('Tribes','Peoples','Kingdoms','Chiefdoms','Kipchaks','Principalities','Emirates')) else 'the '
    for suf in ['','_neutrality','_democratic','_fascism','_communism']:
        loc.append(f' {tag}{suf}:0 "{name}"'); loc.append(f' {tag}{suf}_DEF:0 "{the}{name}"'); loc.append(f' {tag}{suf}_ADJ:0 "{adj}"')
    # flags
    img=Image.new('RGBA',(82,52),col+(255,)); d=ImageDraw.Draw(img)
    lum=0.3*col[0]+0.59*col[1]+0.11*col[2]
    fg=(30,30,30,255) if lum>170 else (245,235,200,255)
    if tag=='JRS':
        img=Image.new('RGBA',(82,52),(250,250,250,255)); d=ImageDraw.Draw(img); gold=(220,170,30,255)
        d.rectangle([37,6,44,46],fill=gold); d.rectangle([21,22,60,29],fill=gold)
        for cx,cy in [(20,13),(61,13),(20,39),(61,39)]:
            d.rectangle([cx-1,cy-6,cx+2,cy+6],fill=gold); d.rectangle([cx-5,cy-1,cx+6,cy+2],fill=gold)
    elif rel=='catholic':
        d.rectangle([36,0,45,51],fill=fg); d.rectangle([0,21,81,30],fill=fg)
    elif rel=='orthodox':
        d.rectangle([0,26,81,51],fill=tuple(int(c*0.6) for c in col)+(255,))
        d.rectangle([38,8,43,44],fill=fg); d.rectangle([28,16,53,20],fill=fg); d.rectangle([30,30,51,34],fill=fg)
    elif rel in ('sunni','shia'):
        d.ellipse([24,10,56,42],fill=fg); d.ellipse([31,8,63,40],fill=col+(255,))
        if rel=='shia': d.rectangle([0,44,81,51],fill=(40,120,60,255))
    else:
        d.rectangle([0,0,81,12],fill=tuple(int(c*0.6) for c in col)+(255,)); d.rectangle([0,39,81,51],fill=tuple(int(c*0.6) for c in col)+(255,))
        d.ellipse([33,18,48,33],fill=fg)
    for sub,size in [('',(82,52)),('medium/',(41,26)),('small/',(10,7))]:
        p=os.path.join(OUT,'gfx/flags',sub); os.makedirs(p,exist_ok=True)
        (img if sub=='' else img.resize(size,Image.LANCZOS)).save(os.path.join(p,tag+'.tga'))
w('common/country_tags/dv_countries.txt','\n'.join(tags)+'\n')
# religions as national spirits (placeholder until real religion mechanic)
REL={'catholic':('Catholic','The Pope in Rome is the head of the Church.'),'orthodox':('Orthodox','The Patriarch of Constantinople guides the faithful.'),
'sunni':('Sunni Islam','The Abbasid Caliph in Baghdad is the nominal head of the faithful.'),'shia':('Shia Islam','The followers of Ali.'),
'pagan':('Old Gods','The old gods of forest and field are still worshipped here.'),'tengri':('Tengrism','The Eternal Blue Sky rules over the steppe.'),
'dharmic':('Eastern Faiths','Buddhist, Hindu and Confucian traditions shape this realm.'),'native':('Native Faiths','Local traditions far from the Holy Land.')}
ideas='ideas = {\n\tcountry = {\n'
for k,(n,dsc) in REL.items():
    ideas+=f'\t\tdv_{k} = {{\n\t\t\tpicture = generic_morale_bonus\n\t\t\tallowed = {{ always = no }}\n\t\t\tremoval_cost = -1\n\t\t\tmodifier = {{ }}\n\t\t}}\n'
    loc.append(f' dv_{k}:0 "{n}"'); loc.append(f' dv_{k}_desc:0 "{dsc}"')
ideas+='\t}\n}\n'
w('common/ideas/dv_religions.txt',ideas)
# bookmark
majors=['JRS','AYB','AGV','FRK','HRE','BYZ','RUM']
bm='bookmarks = {\n\tbookmark = {\n\t\tname = "DV_BOOKMARK_1187"\n\t\tdesc = "DV_BOOKMARK_1187_DESC"\n\t\tdate = 1187.7.4.12\n\t\tpicture = "GFX_select_date_1936"\n\t\tdefault_country = "JRS"\n\t\tdefault = yes\n'
for m in majors:
    bm+=f'\t\t{m} = {{\n\t\t\thistory = "DV_{m}_BOOKMARK_DESC"\n\t\t\tideology = neutrality\n\t\t\tideas = {{ }}\n\t\t\tfocuses = {{ }}\n\t\t}}\n'
bm+='\t\t"---" = {\n\t\t\thistory = "DV_OTHER_BOOKMARK_DESC"\n\t\t}\n'
for m in ['SCL','HNG','CAS','ALM','ABS','GRG','PLD','KYV']:
    bm+=f'\t\t{m} = {{\n\t\t\tminor = yes\n\t\t\thistory = "DV_OTHER_BOOKMARK_DESC"\n\t\t\tideology = neutrality\n\t\t\tideas = {{ }}\n\t\t\tfocuses = {{ }}\n\t\t}}\n'
bm+='\t\teffect = {\n\t\t\trandomize_weather = 22345\n\t\t}\n\t}\n}\n'
w('common/bookmarks/dv_1187.txt',bm)
BD={'JRS':"4 July 1187. King Guy has marched the whole army of Jerusalem out to relieve Tiberias. Saladin waits at the Horns of Hattin.",
'AYB':"Saladin has united Egypt and Syria under one banner. Now the Franks have left their walls behind.",
'AGV':"Henry II rules from the Scottish border to the Pyrenees. The fall of Jerusalem will put the cross in his son's hands.",
'FRK':"Young Philip Augustus wants to break the Angevin hold on France, but the call to crusade may come first.",
'HRE':"Frederick Barbarossa, the old emperor, has one last campaign left in him.",
'BYZ':"Isaac II Angelos holds a weakened empire, threatened by Bulgarian rebels, Sicilian fleets and crusading armies alike.",
'RUM':"Kilij Arslan II has beaten Byzantium at Myriokephalon, but his sons are already fighting over his realm."}
loc+=[' DV_BOOKMARK_1187:0 "The Third Crusade"',' DV_BOOKMARK_1187_DESC:0 "July 1187. Saladin has invaded the Kingdom of Jerusalem, and Europe is about to take the cross."',' DV_OTHER_BOOKMARK_DESC:0 "A realm caught up in the struggle for the Holy Land."']
loc+=[f' DV_{k}_BOOKMARK_DESC:0 "{v}"' for k,v in BD.items()]
w('localisation/english/dv_countries_l_english.yml','\n'.join(loc)+'\n',bom=True)
w('common/defines/dv_defines.lua','NDefines.NGame.START_DATE = "1187.7.4.12"\nNDefines.NGame.END_DATE = "1300.1.1.1"\n')
print('done',len(tags),'countries')
