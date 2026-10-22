# Writes the flags, the leader portraits and their sprites, and sets each country's leader.
# Runs in place on the repo (no vanilla files needed):  python3 tools/gen_heraldry.py
import os,re,struct,sys
from PIL import Image
sys.path.insert(0,os.path.dirname(__file__))
from nations import N
from heraldry import draw_flag
from portraits import draw_portrait

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def save_dds(img,path):
    """Uncompressed 32-bit BGRA DDS, which HoI4 reads without mipmaps."""
    img=img.convert('RGBA'); w,h=img.size
    hdr=struct.pack('<4s7I44x8II16x',b'DDS ',124,0x1|0x2|0x4|0x8|0x1000,h,w,w*4,0,0,
                    32,0x41,0,32,0x00ff0000,0x0000ff00,0x000000ff,0xff000000,0x1000)
    r,g,b,a=img.split()
    with open(path,'wb') as f: f.write(hdr+Image.merge('RGBA',(b,g,r,a)).tobytes())

def leader_block(tag):
    name=N[tag][6]
    return f'''create_country_leader = {{
	name = "{name}"
	desc = ""
	picture = GFX_portrait_dv_{tag}
	expire = "1300.1.1.1"
	ideology = despotism
	traits = {{ }}
}}
'''

if __name__=='__main__':
    os.makedirs(os.path.join(ROOT,'gfx/leaders/DV'),exist_ok=True)
    sprites=[]
    for tag in N:
        img=draw_flag(tag)
        for sub,size in [('',(82,52)),('medium/',(41,26)),('small/',(10,7))]:
            p=os.path.join(ROOT,'gfx/flags',sub); os.makedirs(p,exist_ok=True)
            (img if sub=='' else draw_flag(tag,*size)).save(os.path.join(p,tag+'.tga'))
        save_dds(draw_portrait(tag),os.path.join(ROOT,f'gfx/leaders/DV/{tag}.dds'))
        sprites.append(f'\tspriteType = {{ name = "GFX_portrait_dv_{tag}" texturefile = "gfx/leaders/DV/{tag}.dds" }}')
        # swap the leader in the country's history file
        hist=[f for f in os.listdir(os.path.join(ROOT,'history/countries')) if f.startswith(tag+' - ')]
        for f in hist:
            p=os.path.join(ROOT,'history/countries',f); s=open(p,encoding='utf-8-sig').read()
            s=re.sub(r'\ncreate_country_leader = \{.*?\n\}\n','\n',s,flags=re.S)
            s=re.sub(r'(set_popularities = \{.*?\n\}\n)',lambda m:m.group(1)+'\n'+leader_block(tag),s,count=1,flags=re.S)
            open(p,'w',encoding='utf-8').write(re.sub(r'\n{3,}','\n\n',s))
    open(os.path.join(ROOT,'interface/dv_portraits.gfx'),'w').write('spriteTypes = {\n'+'\n'.join(sprites)+'\n}\n')
    print('flags and portraits for',len(N),'tags')
