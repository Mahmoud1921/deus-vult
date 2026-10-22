import re,glob,os,json
from nations import N
A={int(k):v for k,v in json.load(open('assign.json')).items()}
OUT='out_army'; import shutil; shutil.rmtree(OUT,ignore_errors=True)
def w(p,s,bom=False):
    p=os.path.join(OUT,p); os.makedirs(os.path.dirname(p),exist_ok=True)
    open(p,'w',encoding='utf-8-sig' if bom else 'utf-8',newline='\n').write(s)
land=set()
for l in open('v/map/definition.csv',encoding='latin-1'):
    p=l.split(';')
    if len(p)>4 and p[0].isdigit() and p[4]=='land': land.add(int(p[0]))
sprov={};manp={}
for f in glob.glob('out/history/states/*.txt'):
    t=open(f,encoding='utf-8-sig').read()
    sid=int(re.search(r'\bid\s*=\s*(\d+)',t).group(1))
    manp[sid]=int(re.search(r'manpower\s*=\s*(\d+)',t).group(1))
    vps=[int(x) for x in re.findall(r'victory_points\s*=\s*\{\s*(\d+)',t)]
    provs=[int(x) for x in re.search(r'provinces\s*=\s*\{([^}]*)\}',t).group(1).split()]
    sprov[sid]=[p for p in vps+provs if p in land]
owned={}
for s,tg in A.items(): owned.setdefault(tg,[]).append(s)
# divisions per template: (feudal/askar/horde/warband, knights, siege)
BIG={'AYB':(8,4,1),'HRE':(7,3,1),'AGV':(7,3,1),'FRK':(5,3,1),'BYZ':(6,2,1),'ALM':(6,3,1),'RUM':(4,2,0),'JRS':(5,2,0),
'SCL':(3,1,1),'HNG':(4,1,0),'CAS':(3,1,0),'ABS':(2,1,0),'GRG':(3,1,0),'SLJ':(3,1,0),'KHW':(3,2,0),'GHR':(3,2,0),'CUM':(5,0,0),
'VSZ':(3,1,0),'KYV':(2,1,0),'PLD':(3,1,0),'DNK':(3,1,0),'LEO':(2,1,0),'ARN':(2,1,0),'PRT':(2,1,0),'BLG':(2,1,0),'SRB':(2,0,0),
'ILD':(2,1,0),'VNC':(2,0,1),'PSA':(1,0,0),'PPS':(1,0,0),'TRP':(2,1,0),'ANT':(2,1,0),'CIL':(2,1,0),'CYK':(1,0,0),'SCT':(2,0,0),
'NRW':(2,0,0),'SWD':(2,0,0),'NVG':(3,0,0),'JIN':(5,2,1),'SOG':(6,0,1),'KRK':(3,2,0),'XXA':(2,1,0),'JPN':(3,1,0),'GRY':(2,0,0),'KHR':(3,0,0)}
STEPPE={'CUM','KIP','MGT','KRK','SBT'}
def kind(tag,rel):
    if tag in STEPPE: return 'horde'
    if rel in ('pagan','native') or tag in ('NJD','UYN','GHN','BNT','ABY','MKR','SAP','ICL','PHL','OCN','AMZ','ADN','NAM','MSA','FNT','PRS','LTH','LVN','ESN','GWY','IRK'): return 'warband'
    if rel in ('sunni','shia'): return 'askar'
    if rel=='dharmic': return 'askar'
    return 'feudal'
TPL={
'feudal':('Feudal Host',[('infantry',0,3),('dv_archers',1,2),('cavalry',2,2)]),
'askar':('Askar',[('infantry',0,2),('dv_archers',1,2),('cavalry',2,3)]),
'horde':('Horde',[('cavalry',0,3),('cavalry',1,3),('dv_archers',2,2)]),
'warband':('Warband',[('infantry',0,3),('dv_archers',1,1)]),
'knights':('Knights',[('cavalry',0,2),('cavalry',1,2)]),
'siege':('Siege Train',[('infantry',0,2),('artillery_brigade',1,2)]),
}
def tpl(key,name):
    _,regs=TPL[key]; r=''
    for u,x,n in regs:
        for y in range(n): r+=f'\t\t{u} = {{ x = {x} y = {y} }}\n'
    return f'division_template = {{\n\tname = "{name}"\n\n\tregiments = {{\n{r}\t}}\n}}\n\n'
summary={}
for tag,(name,adj,g,col,cap,rel,leader,_) in N.items():
    if tag not in owned: continue
    if cap is None or A.get(cap)!=tag: cap=max(owned[tag],key=lambda s:manp[s])
    k=kind(tag,rel)
    main,kn,sg=BIG.get(tag,(2,0,0))
    if k=='warband': kn,sg=0,0
    if k=='horde': kn=0
    loc=sprov[cap][0]
    s=tpl(k,TPL[k][0])
    if kn: s+=tpl('knights','Knights' if rel in('catholic','orthodox') else 'Heavy Cavalry')
    if sg: s+=tpl('siege','Siege Train')
    u='units = {\n'
    def div(t,i): return f'\tdivision = {{\n\t\tname = "{i}. {t}"\n\t\tlocation = {loc}\n\t\tdivision_template = "{t}"\n\t\tstart_experience_factor = 0.3\n\t}}\n'
    for i in range(main): u+=div(TPL[k][0],i+1)
    for i in range(kn): u+=div('Knights' if rel in('catholic','orthodox') else 'Heavy Cavalry',i+1)
    for i in range(sg): u+=div('Siege Train',i+1)
    u+='}\n\ninstant_effect = {\n\tadd_equipment_to_stockpile = {\n\t\ttype = infantry_equipment_0\n\t\tamount = %d\n\t\tproducer = %s\n\t}\n}\n' % (300*(main+kn)+200,tag)
    w(f'history/units/{tag}_1187.txt',s+u)
    summary[tag]=(k,main,kn,sg)
# archers sub-unit
w('common/units/dv_archers.txt','''sub_units = {

	dv_archers = {
		abbreviation = "ARC"
		sprite = infantry
		map_icon_category = infantry

		priority = 590
		ai_priority = 150
		active = yes

		type = {
			infantry
		}

		group = infantry

		categories = {
			category_front_line
			category_light_infantry
			category_all_infantry
			category_army
		}

		combat_width = 2

		max_strength = 20
		max_organisation = 50
		default_morale = 0.3
		manpower = 800

		training_time = 120
		suppression = 1
		weight = 0.4

		supply_consumption = 0.05

		soft_attack = 0.2
		defense = -0.2

		need = {
			infantry_equipment = 80
		}
	}
}
''')
loc='''l_english:
 infantry:0 "Men-at-Arms"
 infantry_desc:0 "Foot soldiers in mail with spear, sword and shield. The backbone of any host."
 cavalry:0 "Knights"
 cavalry_desc:0 "Armoured horsemen: Frankish knights, Byzantine kataphraktoi or Turkish and Mamluk heavy cavalry. Expensive, fast and decisive in the charge."
 artillery_brigade:0 "Siege Engines"
 artillery_brigade_desc:0 "Mangonels, trebuchets and the engineers to build them. Slow, but they break walls."
 dv_archers:0 "Archers"
 dv_archers_desc:0 "Bowmen and crossbowmen. They hit hard at range but are lightly armoured."
 infantry_equipment:0 "Arms and Armour"
 infantry_equipment_desc:0 "Spears, swords, shields, mail and horses: everything a host needs to take the field."
 infantry_equipment_0:0 "Arms and Armour"
 infantry_equipment_0_short:0 "Arms"
 infantry_equipment_0_desc:0 "Spears, swords, shields, mail and horses."
 infantry_equipment_1:0 "Improved Arms and Armour"
 infantry_equipment_1_short:0 "Imp. Arms"
 artillery_equipment:0 "Siege Engines"
 artillery_equipment_desc:0 "Mangonels and trebuchets for battering walls."
 artillery_equipment_1:0 "Trebuchet"
 artillery_equipment_1_short:0 "Trebuchet"
 artillery_equipment_1_desc:0 "A counterweight engine that hurls stones against walls and gates."
'''
w('localisation/english/replace/dv_units_l_english.yml',loc,bom=True)
json.dump(summary,open('army_summary.json','w'))
from collections import Counter
print(len(summary),'oobs', sum(a+b+c for _,a,b,c in summary.values()),'divisions', Counter(v[0] for v in summary.values()))
