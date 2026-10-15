"""Read-only asset measurements and diagnostic hand-detail sheet; no artwork modification."""
from pathlib import Path
import json,struct
from PIL import Image,ImageDraw,ImageFont
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/phase2c'
art=Image.open(ROOT/'public/art/durga-lion.png');nebula=Image.open(ROOT/'public/art/cosmic-background.png')
b=(ROOT/'public/art/trishul/keshav/trishul-flight.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);binary=b[28+n:];primitive=g['meshes'][0]['primitives'][0];a=g['accessors'][primitive['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']]
p=np.ndarray((a['count'],3),dtype='<f4',buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',12),4)).copy()
# The optimized GLB uses node transforms already baked into geometry.
shaft=p[(p[:,1]>3.15)&(p[:,1]<3.35)]
report={'character':{'path':'public/art/durga-lion.png','size':art.size,'mode':art.mode,'has_alpha':'A' in art.getbands(),'transparent_pixels':0,'transparent_metadata':art.info.get('transparency'),'checkerboard':'Opaque alternating neutral gray pixels; not a viewer transparency grid','limits':['No prepared empty receiving grip','No separate foreground fingers, thumb or palm mask','Weapons and accessories already painted into other gripping hands','Fixed front view, baked illustrative highlights and no depth/normal data']},'cosmic':{'size':nebula.size,'mode':nebula.mode,'type':'asset-sheet atlas','usable_panel_pixels':[890,8,1530,350],'usable_panel_size':[640,342]},'flight_glb':{'bytes':len(b),'vertices':len(p),'triangles':g['accessors'][primitive['indices']]['count']//3,'bounds':[p.min(axis=0).tolist(),p.max(axis=0).tolist()],'materials':g['materials'],'nodes':g['nodes'],'shaft_slice_bounds':[shaft.min(axis=0).tolist(),shaft.max(axis=0).tolist()] if len(shaft) else None},'diagnostic_target':{'pixel':[985,775],'chosen_hand':'viewer-right lower hand resting above knee; best unoccupied palm in this artwork, not a prepared grip','world':[4.85625,21.65625,-252.9],'shaft_local':[0,3.25,0],'gap_z':.1,'contact_time':19.3,'grip_validated':False,'pulse_allowed':False}}
(OUT/'asset-readiness.json').write_text(json.dumps(report,indent=2))
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',21);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
sheet=Image.new('RGB',(1280,600),'#11111a');d=ImageDraw.Draw(sheet)
crops=[('Potential palm / not a grip',(925,710,1040,840)),('Blessing hand / open',(650,480,770,685)),('Existing bow grip / occupied',(310,575,445,735)),('Baked checkerboard',(0,0,160,160))]
for i,(label,box) in enumerate(crops):
 x=i*320;im=art.crop(box);im.thumbnail((300,390));scale=min(300/(box[2]-box[0]),390/(box[3]-box[1]));im=art.crop(box).resize((round((box[2]-box[0])*scale),round((box[3]-box[1])*scale)),Image.Resampling.NEAREST);sheet.paste(im,(x+10,65));d.text((x+10,15),label,font=small,fill='#efdfbe');d.text((x+10,475),f'Original crop: {box[2]-box[0]} x {box[3]-box[1]} px',font=small,fill='#efdfbe')
 if i==0:d.text((x+10,510),'Target pixel: (985, 775)',font=small,fill='#efdfbe')
d.text((15,560),'Inspection enlargements only. Original artwork and alpha remain unchanged.',font=font,fill='#efdfbe');sheet.save(OUT/'asset-detail-contact.png')
print(json.dumps({'character':report['character'],'target':report['diagnostic_target'],'shaft':report['flight_glb']['shaft_slice_bounds']},indent=2))
