# Contact sheet to check the sampled colors by eye: python sheet.py <start> <count> [out.png]
import json,sys
from PIL import Image, ImageDraw
d=[c for c in json.load(open('chapters_auto.json',encoding='utf-8')) if c['colors']]
start,n=int(sys.argv[1]),int(sys.argv[2]); d=d[start:start+n]
W,H=300,130; cols=4
sheet=Image.new('RGB',(W*cols,H*((len(d)+cols-1)//cols)),'#808080'); dr=ImageDraw.Draw(sheet)
for i,c in enumerate(d):
    x,y=(i%cols)*W,(i//cols)*H
    im=Image.open(c['img']).convert('RGBA'); im.thumbnail((90,H-4)); sheet.paste(im,(x+2,y+2),im)
    dr.text((x+95,y+2),c['name'][:30],fill='white')
    xx=x+95
    for hx,s in c['colors']:
        w=max(8,int(190*s)); dr.rectangle([xx,y+20,xx+w,y+60],fill=hx); xx+=w

sheet.save(sys.argv[3] if len(sys.argv) > 3 else "sheet.png")
