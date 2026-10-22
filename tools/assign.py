from nations import N
rows=[l.rstrip('\n').split('\t') for l in open('s.tsv')]
A={}
for t,v in N.items():
    for s in v[7]: A[s]=t
HRE_OWN={'GER','AUS','CZE','HOL','BEL','LUX','SWI','FRA','ITA','YUG'}
def outside(o,x,y):
    if y>1850 and 1900<x<2700: return 'ICL'
    if x<2400:
        if y>=1300: return 'NAM'
        if y>=950: return 'MSA'
        return 'ADN' if x<1720 else 'AMZ'
    if x<2620 and y>1750: return 'ICL'
    if 2620<=x<3800 and y>1750: return 'SAP' if x<3400 else 'NVG'
    if 2400<=x<3800 and y<1000:
        if x>3330 and y>650 and o not in ('SAU','OMA','YEM'): return 'ABY'
        if o in ('SAU','OMA'): return 'NJD'
        if o=='YEM': return 'AYB'
        if 3150<=x<=3330 and 850<=y: return 'MKR'
        if y>=780 and x<3200: return 'GHN'
        return 'BNT'
    if 2400<=x<3800: return 'ALM'  # canaries etc
    # asia x>=3800
    if o in ('SOV','TAN'):
        if o=='TAN': return 'MGT'
        if y>=1560: return 'SBT'
        if x<4250 and y>=1380: return 'KIP'
        if x<4250: return 'KRK'
        return 'SBT'
    if o=='MON': return 'MGT'
    if o=='SIK': return 'KRK'
    if o=='TIB': return 'TBT'
    if o=='AFG': return 'GHR'
    if o=='YUN': return 'DAL'
    if o=='XSM' or (o in('CHI','PRC','SHX','MEN') and x<4470 and y>1200): return 'XXA'
    if o in ('CHI','PRC','GXC','SHX','MEN','MAN'):
        return 'JIN' if y>=1250 else 'SOG'
    if o=='JAP':
        if y>=1450: return 'SBT'
        if x>=4820: return 'JPN'
        if y<1100: return 'PHL'
        return 'GRY'
    if o=='SIA': return 'KHR'
    if o=='BRM': return 'PGN'
    if o=='PHI': return 'PHL'
    if o in ('AST','NZL'): return 'OCN'
    if o in ('MAL','INS'): return 'SRV'
    if 3800<=x<4300 and y<1200 and y>=700:
        if x<3990 and y>=1060: return 'GHR'
        return 'HND' if y>=950 else 'DCN'
    if 4300<=x and 1000<=y<1150 and x<4500: return 'DVT' if x>4380 else 'PGN'
    if 4300<=x<4500 and 850<=y<1000: return 'KHR'
    if x>=4300 and 550<=y<900 and x<4950: return 'SRV'
    if y<700: return 'OCN'
    return None
EXTRA={856:'AYB',659:'AYB',992:'AYB',178:'ALM',326:'SOG',728:'SOG',729:'SOG',441:'HND',787:'HND',442:'GHR',632:'OCN',638:'OCN',650:'SBT'}
A.update(EXTRA)
left=[]
for sid,name,o,cat,x,y,f in rows:
    sid=int(sid);x=int(x);y=int(y)
    if sid in A: continue
    inbox=2550<=x<=3800 and 1000<=y<=1800
    if inbox and o in HRE_OWN: A[sid]='HRE'; continue
    if not inbox:
        t=outside(o,x,y)
        if t: A[sid]=t; continue
    left.append((sid,name,o,x,y))
import json; json.dump(A,open('assign.json','w'))
print('assigned',len(A),'left',len(left))
for l in left: print(l)
from collections import Counter
print(sorted(Counter(A.values()).items(), key=lambda k:-k[1]))
