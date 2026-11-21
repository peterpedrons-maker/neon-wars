# Esboço oficial (proposta) da REGIÃO 2 — Cinzamuro. Rodar: /usr/bin/python3 tools/mmo/esboco_regiao2.py  -> docs/regiao2_esboco.png
from PIL import Image,ImageDraw,ImageFont
W,H=1300,2740
im=Image.new('RGB',(W,H),(30,24,20));d=ImageDraw.Draw(im)
FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';FR='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f=lambda s,b=1:ImageFont.truetype(FB if b else FR,s)
d.text((W//2,38),"REGIÃO 2 — TERRAS ÁRIDAS DE CINZAMURO",font=f(30),fill=(255,214,130),anchor='mm')
d.text((W//2,76),"(esboço · norte para cima · níveis 10–20 · ☠ chefe de zona · ◆ entrada de dungeon)",font=f(17,0),fill=(200,190,170),anchor='mm')
CA,LI,ES=0,1,2
OUT={CA:(255,255,255),LI:(236,206,140),ES:(110,225,215)}
# nome:(cx,cy,w,h,cor,nivel,tipo,extra)
Z={
 'Portão do Deserto → Região 3':(650,290,380,110,(110,96,86),'Nv 19–20',CA,'guarda + missão de 3 chefes'),
 'Vale das Forjas Mortas':(650,600,460,260,(98,58,52),'Nv 18–20',CA,'☠ Titã de Magma · ◆ Forja de Pedranegra'),
 'Gruta de Obsidiana (secreta)':(1010,420,240,100,(52,50,62),'Nv 19–20',ES,''),
 'Desfiladeiro Rubro':(650,830,260,100,(150,70,52),'Nv 17–18',LI,''),
 'Campo dos Cercos':(250,820,320,200,(112,104,114),'Nv 17–19',CA,'☠ Marechal Sem-Nome · ◆ Bastilha Negra'),
 'Acampamento dos Saqueadores (s.)':(250,630,260,100,(96,82,70),'Nv 17–18',ES,''),
 'Caminho dos Cercos':(250,1040,240,100,(140,120,96),'Nv 16–17',LI,''),
 'Salinas Brancas':(650,1040,460,260,(222,222,214),'Nv 15–17',CA,'☠ Rainha Escorpião · ◆ Minas de Sal'),
 'Ruínas do Sol Caído':(1040,820,320,200,(204,166,92),'Nv 16–18',CA,'☠ Hierofante Solar · ◆ Templo do Sol'),
 'Covil do Verme (secreta)':(1040,630,240,100,(120,96,70),'Nv 18–19',ES,'◆ Ninho do Verme'),
 'Trilha dos Abutres':(1040,1040,240,100,(150,126,92),'Nv 15–16',LI,''),
 'Leito do Rio Seco':(650,1290,260,100,(160,130,94),'Nv 14–15',LI,''),
 'Cisterna Antiga (secreta)':(250,1290,240,100,(80,92,100),'Nv 14–15',ES,''),
 'Mesas Rubras':(650,1520,460,260,(168,84,58),'Nv 13–15',CA,'☠ Rei das Mesas (troll)'),
 'Tumba do Nômade (secreta)':(1080,1520,240,100,(110,92,76),'Nv 14–15',ES,''),
 'Garganta do Vento':(650,1760,260,100,(150,120,90),'Nv 12–13',LI,''),
 'Mirante dos Abutres (s.)':(240,1790,240,100,(120,100,84),'Nv 12–13',ES,''),
 'Cânion do Eco':(240,1960,320,200,(150,96,70),'Nv 12–14',CA,'☠ Capitão Vento-Seco'),
 'Planalto Árido':(650,1960,460,280,(176,142,98),'Nv 10–12',CA,'☠ Matriarca Escorpião'),
 'Oásis Escondido (secreta)':(1060,1960,240,100,(70,130,110),'Nv 11–12',ES,''),
 'Estrada da Muralha':(650,2200,260,100,(150,126,92),'Nv 10–11',LI,''),
 'CINZAMURO (cidade-fortaleza)':(650,2390,400,130,(150,110,80),'Nv 10 · hub',CA,'3 bairros: Ordem · Guildas · Remanescentes'),
 'Passo da Montanha (Região 1)':(650,2590,340,100,(112,112,118),'Nv 8–10',CA,''),
}
MAIN=[[(650,2540),(650,2455)],[(650,2325),(650,2250)],[(650,2150),(650,2100)],[(650,1820),(650,1810)],[(650,1710),(650,1650)],[(650,1390),(650,1340)],[(650,1240),(650,1170)],[(650,910),(650,880)],[(650,780),(650,730)],[(650,470),(650,345)]]
SIDE=[[(420,1960),(400,1960)],[(240,1860),(240,1840)],[(880,1520),(970,1520)],[(880,1040),(920,1040)],[(1040,990),(1040,920)],[(420,1040),(370,1040)],[(250,990),(250,920)],[(1040,720),(1040,680)],[(250,720),(250,680)],[(540,1290),(370,1290)],[(880,600),(900,470)]]
SECRET=[[(880,1960),(950,1960)]]
def road(pts,col,w):
    d.line(pts,fill=col,width=w,joint='curve')
    for t in(pts[0],pts[-1]):
        d.ellipse([t[0]-7,t[1]-7,t[0]+7,t[1]+7],fill=(250,250,240),outline=(20,20,20),width=3)
for p in SIDE:road(p,(176,146,100),12)
for p in SECRET:road(p,(90,170,165),9)
for p in MAIN:road(p,(255,206,70),18)
for n,(cx,cy,w,h,c,lv,k,ex) in Z.items():
    r=[cx-w//2,cy-h//2,cx+w//2,cy+h//2]
    d.rounded_rectangle(r,radius=26,fill=c,outline=OUT[k],width=4)
    dark=sum(c)<420
    tc=(255,255,255) if dark else (30,24,20); sc=(15,15,15) if dark else (255,255,255)
    big=k==CA
    d.text((cx,cy-(22 if ex else 12)),n.replace(' (secreta)','').replace(' (s.)',''),font=f(19 if big else 16),fill=tc,anchor='mm',stroke_width=3,stroke_fill=sc)
    d.text((cx,cy+(2 if ex else 14)),lv+(' · secreta' if k==ES else ''),font=f(16),fill=(255,226,120) if dark else (110,60,10),anchor='mm',stroke_width=3,stroke_fill=sc)
    if ex:d.text((cx,cy+26),ex,font=f(14,0),fill=tc,anchor='mm',stroke_width=2,stroke_fill=sc)
# legenda
y=H-70
for lab,col,wd in(('caminho principal',(255,206,70),18),('ligações / desvios',(176,146,100),12),('zonas secretas',(90,170,165),9)):
    pass
d.line([(60,H-40),(120,H-40)],fill=(255,206,70),width=14);d.text((132,H-40),"caminho principal",font=f(15,0),fill=(230,220,200),anchor='lm')
d.line([(380,H-40),(440,H-40)],fill=(176,146,100),width=10);d.text((452,H-40),"ligações / desvios",font=f(15,0),fill=(230,220,200),anchor='lm')
d.line([(700,H-40),(760,H-40)],fill=(90,170,165),width=8);d.text((772,H-40),"zonas secretas",font=f(15,0),fill=(230,220,200),anchor='lm')
im.save('docs/regiao2_esboco.png');print(im.size)
