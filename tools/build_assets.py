#!/usr/bin/env python3
"""Generate bespoke animated GIF visuals for Mehdi Rostami's GitHub README.

Requirements: Pillow, NumPy. Run from any location: python tools/build_assets.py
GIFs intentionally use no JS, CSS, external SVG fonts or hosted animation services.
"""
from __future__ import annotations
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
ASSETS.mkdir(parents=True,exist_ok=True)

INTER='/usr/share/fonts/opentype/inter/'
MONO='/usr/share/fonts/truetype/croscore/Cousine-Regular.ttf'
MONOB='/usr/share/fonts/truetype/croscore/Cousine-Bold.ttf'
FONTS={
 'display':INTER+'InterDisplay-Black.otf',
 'heavy':INTER+'Inter-ExtraBold.otf',
 'bold':INTER+'Inter-Bold.otf',
 'semibold':INTER+'Inter-SemiBold.otf',
 'medium':INTER+'Inter-Medium.otf',
 'regular':INTER+'Inter-Regular.otf',
 'mono': MONO,
 'monob': MONOB,
}

def font(kind,size):
    # The packaged GIFs work without this script. For regeneration, use the
    # bundled style's Inter/Cousine font paths when available; otherwise
    # fall back to ubiquitous sans-serif/monospace system fonts.
    primary=FONTS[kind]
    fallback='DejaVuSansMono.ttf' if kind in ('mono','monob') else 'DejaVuSans.ttf'
    try: return ImageFont.truetype(primary,size)
    except OSError: return ImageFont.truetype(fallback,size)


def c(hexcolor, alpha=255):
 h=hexcolor.lstrip('#');return tuple(int(h[i:i+2],16) for i in (0,2,4))+(int(alpha),)

def text(draw,xy,words,font_obj,fill,anchor=None,spacing=0):
 if not spacing:
  draw.text(xy,words,font=font_obj,fill=fill,anchor=anchor)
  return
 x,y=xy
 for letter in words:
  draw.text((x,y),letter,font=font_obj,fill=fill,anchor='lt')
  x+=draw.textlength(letter,font=font_obj)+spacing

def stroke_line(draw,points,fill,width=1):draw.line(points,fill=fill,width=width,joint='curve')

def base_background(w,h,theme='dark',bloom=True):
 yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
 base=np.array([7,12,25],np.float32)
 top=np.stack([2.2 + 1.3*xx/w, 4.0+1.5*xx/w, 8.5+1.3*xx/w],axis=-1)
 dist=np.sqrt(((xx-w*.79)/(w*.50))**2+((yy-h*.50)/(h*.87))**2)
 halo=np.exp(-(dist*dist)*3)
 violet=np.exp(-(((xx-w*.96)/(w*.55))**2+((yy-h*.21)/(h*.75))**2)*3)
 arr=base+top+halo[...,None]*np.array([14,19,39])+violet[...,None]*np.array([9,2,25])
 arr+=np.clip(xx/w,0,1)[...,None]*np.array([1,4,7])
 arr=np.uint8(np.clip(arr,0,255))
 return Image.fromarray(arr,'RGB').convert('RGBA')

def rounded_overlay(layer,box,radius,fill,outline=None,width=1):
 d=ImageDraw.Draw(layer,'RGBA');d.rounded_rectangle(box,radius=radius,fill=fill,outline=outline,width=width)

def draw_corner_marks(d,w,h):
 hi=c('#48DDE2',145);dim=c('#587197',75)
 # subtle border, clipped-tech corners
 d.line([(33,23),(33,52)],fill=hi,width=2);d.line([(33,23),(62,23)],fill=hi,width=2)
 d.line([(w-36,23),(w-65,23)],fill=dim,width=2);d.line([(w-36,23),(w-36,52)],fill=dim,width=2)
 d.line([(32,h-25),(64,h-25)],fill=dim,width=2);d.line([(32,h-25),(32,h-56)],fill=dim,width=2)
 d.line([(w-35,h-25),(w-65,h-25)],fill=hi,width=2);d.line([(w-35,h-25),(w-35,h-56)],fill=hi,width=2)

def gradient_text(base,position,label,font_obj,colors,tracking=0):
 # top-left placement, correct text bounds via full-size mask
 layer=Image.new('L',base.size)
 ld=ImageDraw.Draw(layer)
 x,y=position
 if tracking==0:
  ld.text(position,label,font=font_obj,fill=255,anchor='lt')
 else:
  text(ld,position,label,font_obj,255,spacing=tracking)
 bbox=layer.getbbox()
 if not bbox:return
 left,top,right,bottom=bbox
 h=max(1,right-left)
 grd=np.zeros((base.height,base.width,4),dtype=np.uint8)
 a=np.array(colors[0][:3],float);b=np.array(colors[1][:3],float)
 col=np.array([a*(1-t)+b*t for t in np.linspace(0,1,h)],dtype=np.uint8)
 grd[top:bottom,left:right,:3]=col[np.minimum(np.arange(right-left),h-1)][None,:,:]
 grd[top:bottom,left:right,3]=np.asarray(layer)[top:bottom,left:right]
 base.alpha_composite(Image.fromarray(grd,'RGBA'))

def translucent_dots(d,w,h):
 # fixed quiet dot matrix right, more precise than noisy texture
 for y in range(36,h-18,32):
  for x in range(686,w-20,32):
   fade=1-max(0,abs(x-(w*.77))/(w*.5))*.5
   a=int(16+14*fade)
   d.ellipse((x-.9,y-.9,x+.9,y+.9),fill=c('#779BD0',a))

def stable_hero_layer(w,h):
 im=base_background(w,h)
 d=ImageDraw.Draw(im,'RGBA')
 translucent_dots(d,w,h)
 # cinematic vertical accent/panel with a cutoff
 d.polygon([(744,0),(790,0),(635,h),(597,h)],fill=c('#294368',15))
 d.polygon([(791,0),(805,0),(649,h),(631,h)],fill=c('#4FBFEF',9))
 d.line([(691,39),(691,h-43)],fill=c('#7DA8C6',32),width=1)
 # scan horizontal lines at bottom right
 for y in (68,106,350,392):
  d.line([(747,y),(w-76,y)],fill=c('#4975A3',28),width=1)
 # left side index and tiny decorative indicator
 d.rounded_rectangle((70,57,108,80),radius=6,fill=c('#7CECF2',24),outline=c('#81F4E7',110),width=1)
 text(d,(81,62),'M/',font('monob',13),c('#98FEF5'))
 text(d,(124,60),'INDEPENDENT DIGITAL PROFILE',font('mono',14),c('#A1BCD5'),spacing=.8)
 d.ellipse((535,66,544,75),fill=c('#62EACF',225))
 d.ellipse((531,62,548,79),outline=c('#62EACF',60),width=1)
 # Main name contrasting typography, carefully measured
 text(d,(65,106),'MEHDI',font('display',111),c('#F3F8FF'))
 gradient_text(im,(65,229),'ROSTAMI',font('display',100),(c('#81F7E4'),c('#6093FF')))
 d=ImageDraw.Draw(im,'RGBA')
 # Data Engineer signature and line marker
 d.rounded_rectangle((73,332,87,355),radius=4,fill=c('#59E8DC',230))
 text(d,(103,333),'DATA ENGINEER',font('bold',23),c('#D3F9FC'),spacing=2.0)
 text(d,(73,375),'Turning complex data into dependable systems.',font('medium',19),c('#AEC2D8'))
 d.line([(73,420),(594,420)],fill=c('#6788AC',80),width=1)
 text(d,(73,432),'DATA  /  AUTOMATION  /  INFRASTRUCTURE',font('mono',13),c('#718EAA'),spacing=.5)
 # Small minimap/chip above orb
 d.rounded_rectangle((808,40,1170,77),radius=9,fill=c('#101A30',190),outline=c('#6A90B3',72),width=1)
 d.ellipse((826,53,836,63),fill=c('#69EDCE'))
 text(d,(850,49),'SYSTEMS LAB   /   BUILD MODE',font('monob',13),c('#C6D6E5'),spacing=.4)
 d.line([(33,h-26),(w-36,h-26)],fill=c('#4A699B',70),width=1)
 draw_corner_marks(d,w,h)
 return im

def glow_overlay(base,primitives,blur=8,opacity=1.0):
 lay=Image.new('RGBA',base.size)
 d=ImageDraw.Draw(lay,'RGBA')
 primitives(d)
 b=lay.filter(ImageFilter.GaussianBlur(blur))
 if opacity !=1.0:b.putalpha(b.getchannel('A').point(lambda a:int(a*opacity)))
 base.alpha_composite(b)

def polar(cx,cy,r,angle):return(cx+math.cos(angle)*r,cy+math.sin(angle)*r)

def draw_hero_frame(stable,t):
 im=stable.copy(); w,h=im.size
 cx,cy=1008,248
 ang=t*math.tau
 # A soft diagonal glint sweeps across the gradient wordmark each loop.
 u=(t-.10)/.80
 if 0.0 <= u <= 1.0:
  left,top=65,229
  sw,sh=560,106
  local=Image.new('L',(sw,sh),0)
  ImageDraw.Draw(local).text((0,0),'ROSTAMI',font=font('display',100),fill=255,anchor='lt')
  yy,xx=np.mgrid[0:sh,0:sw].astype(np.float32)
  center=-85+(sw+130)*u
  band=xx-.24*yy-center
  streak=np.exp(-.5*(band/23.)**2)
  alpha=np.asarray(local).astype(np.float32)*streak*(.25+.75*math.sin(math.pi*u))*.45
  overlay=np.zeros((sh,sw,4),dtype=np.uint8)
  overlay[:,:,:3]=[221,255,252]
  overlay[:,:,3]=np.uint8(np.clip(alpha,0,255))
  im.alpha_composite(Image.fromarray(overlay,'RGBA'),(left,top))
 # nested ambient bloom for premium illustration
 glow_overlay(im,lambda d:d.ellipse((cx-160,cy-160,cx+160,cy+160),outline=c('#2D89CF',68),width=14),blur=34,opacity=.6)
 d=ImageDraw.Draw(im,'RGBA')
 d.ellipse((cx-152,cy-152,cx+152,cy+152),fill=c('#0C1B30',135),outline=c('#4D739B',82),width=1)
 d.ellipse((cx-133,cy-133,cx+133,cy+133),outline=c('#476C9C',96),width=2)
 d.ellipse((cx-104,cy-104,cx+104,cy+104),outline=c('#6091B9',70),width=1)
 d.ellipse((cx-67,cy-67,cx+67,cy+67),fill=c('#14223B',214),outline=c('#69E9DA',108),width=2)
 # ring marks + meter calibration
 for i in range(48):
  a=i*math.tau/48
  r1=140 if i%4 else 135;r2=146
  p1=polar(cx,cy,r1,a);p2=polar(cx,cy,r2,a)
  d.line((p1,p2),fill=c('#7DB9D8',90 if i%4==0 else 35),width=2 if i%4==0 else 1)
 # arc glow shimmer
 def arcs(dr):
  for radius,start,span,color in [
   (147,int(t*360+14),59,'#56F5E2'),
   (130,int(-t*260+190),45,'#9B89FF'),
   (106,int(t*180+93),37,'#5AACFF')]:
   dr.arc((cx-radius,cy-radius,cx+radius,cy+radius),start=start,end=start+span,fill=c(color,205),width=4)
 glow_overlay(im,arcs,blur=9,opacity=.8)
 d=ImageDraw.Draw(im,'RGBA')
 arcs(d)
 # dashed flowing spiral tracers -- moving waveform
 for j in range(22):
  a=(j/22)*math.tau + .20*t
  strength=(math.sin(a*2-ang)+1)*.5
  r=124+8*math.sin(j*.55+ang)
  x,y=polar(cx,cy,r,a)
  alpha=int(26+83*strength)
  d.ellipse((x-1.3,y-1.3,x+1.3,y+1.3),fill=c('#B9FFF5',alpha))
 # Orbital satellites + trailing afterglow
 for radius,speed,off,col in [(147,1.0,0,'#8DFFF0'),(130,-1.0,2.3,'#B4A0FF'),(106,0.7,3.1,'#82BFFF')]:
  a=ang*speed+off
  for trail in range(12,0,-1):
   px,py=polar(cx,cy,radius,a-trail*.047*speed)
   rad=max(1,4.0-trail*.28)
   d.ellipse((px-rad,py-rad,px+rad,py+rad),fill=c(col,int((12-trail)*12)))
  px,py=polar(cx,cy,radius,a)
  d.ellipse((px-5,py-5,px+5,py+5),fill=c(col,240))
  d.ellipse((px-9,py-9,px+9,py+9),outline=c(col,70),width=1)
 # Core main icon
 text(d,(cx-38,cy-70),'M',font('display',78),c('#F3FEFF'))
 text(d,(cx-29,cy+31),' / R',font('monob',15),c('#93B0CE'),spacing=1.2)
 # precision radial lines outside ring
 for a0 in (math.pi*.25,math.pi*.88,math.pi*1.31,math.pi*1.84):
  p1=polar(cx,cy,155,a0);p2=polar(cx,cy,183,a0)
  d.line((p1,p2),fill=c('#5D95BE',110),width=1)
  d.ellipse((p2[0]-2,p2[1]-2,p2[0]+2,p2[1]+2),fill=c('#5EE3D9',150))
 # side support data decoration
 text(d,(774,147),'01  /  INGEST',font('mono',11),c('#77A3BF'))
 text(d,(786,164),'●  ●  ●  ●',font('mono',13),c('#56D1E0',120))
 text(d,(1134,346),'SIGNAL',font('monob',11),c('#8CBAD0'))
 # live oscilloscope under orbital core
 pts=[]
 for x in range(766,856,3):
  y=341+8*math.sin((x-766)*.13+ang)+4*math.sin((x-766)*.27-ang)
  pts.append((x,y))
 d.line(pts,fill=c('#5DECD6',170),width=2)
 # animated signal bar lower left
 for n in range(18):
  amplitude=3+7*(.5+.5*math.sin(ang*2+n*.55))
  xx=76+n*8;top=408-amplitude
  d.rounded_rectangle((xx,top,xx+4,412),radius=2,fill=c('#6DF1E0',150+n*3))
 # drifting scanning line through orbital panel only
 scan_y=int(100+(t%1)*277)
 d.line([(777,scan_y),(1178,scan_y)],fill=c('#75D1F7',12),width=1)
 return im.convert('RGB')

def stable_focus_layer(w,h):
 im=base_background(w,h)
 d=ImageDraw.Draw(im,'RGBA')
 for x in (29,424,819):
  d.rounded_rectangle((x,20,x+376,h-21),radius=17,fill=c('#0F1C31',240),outline=c('#416C92',105),width=2)
  d.line([(x+22,20),(x+126,20)],fill=c('#6EE8F2',160),width=3)
 draw_corner_marks(d,w,h)
 return im

def draw_focus_frame(static,t):
 im=static.copy();d=ImageDraw.Draw(im,'RGBA')
 cards=[
  (29,'01','ETL / ELT','PIPELINE ENGINEERING','Data modeling  /  Validation', '#69E5D7'),
  (424,'02','AIRFLOW','WORKFLOW ORCHESTRATION','Scheduling  /  Reliability','#81ABFF'),
  (819,'03','PYSPARK','DISTRIBUTED PROCESSING','Scale  /  Transformations','#AD91FF'),
 ]
 for idx,(x,number,head,sub,small,color) in enumerate(cards):
  d.rounded_rectangle((x+24,40,x+80,66),radius=8,fill=c(color,24),outline=c(color,105),width=1)
  text(d,(x+38,43),number,font('monob',16),c('#091525'))
  text(d,(x+24,79),head,font('bold',31),c('#F5F8FF'))
  text(d,(x+24,127),sub,font('monob',12),c(color))
  text(d,(x+24,162),small,font('regular',16),c('#9DB7CB'))
  # signature radiating activity rings top-right
  xc=x+324;yc=59
  for j in range(2):
   rad=9+j*6+(t*6)%6
   d.ellipse((xc-rad,yc-rad,xc+rad,yc+rad),outline=c(color,100-int(j*26)),width=1)
  d.ellipse((xc-4,yc-4,xc+4,yc+4),fill=c(color,230))
  # small moving glowing segment along bottom
  track_l=x+25;track_r=x+353
  d.line([(track_l,197),(track_r,197)],fill=c('#466884',70),width=2)
  pct=(t+idx*.3)%1
  px=track_l+int((track_r-track_l)*pct)
  d.line([(max(track_l,px-58),197),(px,197)],fill=c(color,200),width=3)
 return im.convert('RGB')

def stable_footer(w,h):
 im=base_background(w,h)
 d=ImageDraw.Draw(im,'RGBA')
 d.line([(29,21),(w-30,21)],fill=c('#5A98BB',90),width=1)
 d.line([(29,h-21),(w-30,h-21)],fill=c('#5A98BB',90),width=1)
 text(d,(40,42),'MR /',font('monob',18),c('#63F3DC'))
 text(d,(117,43),'ENGINEER  ·  AUTOMATE  ·  OPTIMIZE',font('monob',17),c('#D9E4F5'),spacing=.8)
 text(d,(839,43),'ALWAYS IN BUILD MODE',font('mono',14),c('#849EB9'))
 return im

def draw_footer_frame(static,t):
 im=static.copy(); d=ImageDraw.Draw(im,'RGBA');w,h=im.size
 for j in range(12):
  cx=745+j*7
  yy=52
  amp=3+(math.sin(math.tau*t*2+j*.52)+1)*4
  d.rounded_rectangle((cx,yy-amp,cx+3,yy+amp),radius=2,fill=c('#60DEDB',100+int(110*(.5+.5*math.sin(math.tau*t*2+j*.52)))))
 x=w-55;y=49
 d.ellipse((x-5,y-5,x+5,y+5),fill=c('#74F1C6'))
 r=8+4*((t*2)%1)
 d.ellipse((x-r,y-r,x+r,y+r),outline=c('#74F1C6',int(140*(1-(t*2)%1))),width=2)
 return im.convert('RGB')

def generate_gif(frames,path,fps=12,palette_colors=112):
 # Establish a shared palette for all frames: avoids per-frame color shimmer.
 sample=[frames[i].resize((min(440,frames[i].width),min(180,frames[i].height)), Image.Resampling.BILINEAR) for i in range(0,len(frames),max(1,len(frames)//13))]
 sw=max(i.width for i in sample); sh=max(i.height for i in sample)
 montage=Image.new('RGB',(sw,sh*len(sample)),(7,12,22))
 for j,s in enumerate(sample):montage.paste(s,(0,j*sh))
 palette=montage.quantize(colors=palette_colors,method=Image.Quantize.MEDIANCUT)
 paletteimg=Image.new('P',(1,1));paletteimg.putpalette(palette.getpalette())
 quant=[f.quantize(palette=paletteimg,dither=Image.Dither.NONE) for f in frames]
 quant[0].save(path,format='GIF',save_all=True,append_images=quant[1:],duration=round(1000/fps),loop=0,disposal=2,optimize=True)
 print(path, f'{path.stat().st_size/1024/1024:.2f} MiB',len(frames),'frames')

def main():
 import sys
 # Loopable exact 6 seconds; temporal samples sync orbital satellites.
 print('Rendering custom GitHub profile assets...')
 w,h=1200,470
 # Source visual design coordinates use 1200 wide; arc center fits around 1008.
 base=stable_hero_layer(w,h)
 n=60
 frames=[draw_hero_frame(base,i/n) for i in range(n)]
 generate_gif(frames,ASSETS/'hero.gif',fps=12,palette_colors=128)
 frames[12].save(ASSETS/'hero_preview.png',optimize=True)
 del frames
 w,h=1200,240
 base=stable_focus_layer(w,h)
 frames=[draw_focus_frame(base,i/48) for i in range(48)]
 generate_gif(frames,ASSETS/'learning.gif',fps=12,palette_colors=96)
 del frames
 w,h=1200,110
 base=stable_footer(w,h)
 frames=[draw_footer_frame(base,i/48) for i in range(48)]
 generate_gif(frames,ASSETS/'signal.gif',fps=12,palette_colors=84)
 print('Done!')

if __name__=='__main__':main()
