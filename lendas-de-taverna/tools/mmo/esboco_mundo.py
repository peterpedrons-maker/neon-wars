from PIL import Image,ImageDraw,ImageFont
W,H=1100,2240
im=Image.new('RGB',(W,H),(24,30,22));d=ImageDraw.Draw(im)
FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';FR='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f=lambda s,b=1:ImageFont.truetype(FB if b else FR,s)
d.text((W//2,38),"ESBOÇO DO MUNDO v3 — mais zonas secretas e de ligação",font=f(29),fill=(255,226,140),anchor='mm')
d.text((W//2,74),"(proposta · norte para cima · níveis aproximados)",font=f(17,0),fill=(190,200,180),anchor='mm')
CA,LI,ES=0,1,2
OUT={CA:(255,255,255),LI:(236,206,140),ES:(110,225,215)}
Z={ # nome:(cx,cy,w,h,cor,nivel,tipo)
 'Cidade 2 (a definir)':(560,160,320,110,(120,110,150),'~Nv 10+',CA),
 'Passo da Montanha':(560,350,340,150,(120,120,125),'Nv 8–10',CA),
 'Desfiladeiro':(560,540,240,100,(104,104,96),'Nv 7–8',LI),
 'Floresta dos Ogros':(190,500,300,200,(40,92,50),'Nv 5–8',CA),
 'Cemitério':(920,500,280,200,(86,72,110),'Nv 6–9',CA),
 'Colinas Rochosas':(560,720,360,170,(128,124,108),'Nv 4–6',CA),
 'Gruta Aberta (secreta)':(940,860,230,110,(58,66,84),'Nv 7–8',ES),
 'Trilha dos Lenhadores':(190,720,220,100,(70,96,60),'Nv 4–5',LI),
 'Ponte do Rio':(600,905,240,100,(96,120,140),'Nv 3–4',LI),
 'Floresta dos Goblins':(190,930,300,200,(30,78,56),'Nv 3–5',CA),
 'Clareira das Ruínas (secreta)':(150,1130,250,100,(52,84,70),'Nv 4–5',ES),
 'Planície de Brumavale':(640,1130,440,270,(80,138,62),'Nv 1–3',CA),
 'Trilha do Brejo':(380,1360,220,100,(86,98,56),'Nv 3–4',LI),
 'Estrada de Brumavale':(640,1370,240,100,(150,124,84),'Nv 1',LI),
 'Pântano':(210,1580,340,190,(76,92,44),'Nv 4–6',CA),
 'Brumavale (cidade)':(640,1570,320,120,(190,150,90),'Nv 1 · início',CA),
 'Estrada dos Mortos':(905,300,220,100,(96,84,104),'Nv 6–7',LI),
 'Mina Abandonada (secreta)':(190,250,230,110,(70,70,80),'Nv 6–7',ES),
 'Margem do Lago (secreta)':(985,1215,190,100,(70,112,160),'Nv 2–3',ES),
 'Bosque do Eremita (secreta)':(140,1360,200,100,(46,100,60),'Nv 3–4',ES),
 'Cabana da Bruxa (secreta)':(210,1790,240,100,(80,60,90),'Nv 5–6',ES),
}
LS={'Planície de Brumavale':'P','Ponte do Rio':'P','Margem do Lago (secreta)':'P','Pântano':'PE','Colinas Rochosas':'M','Mina Abandonada (secreta)':'M','Passo da Montanha':'M','Gruta Aberta (secreta)':'M',
    'Bosque do Eremita (secreta)':'E','Trilha do Brejo':'E','Cabana da Bruxa (secreta)':'E','Floresta dos Ogros':'LE','Floresta dos Goblins':'L','Trilha dos Lenhadores':'L','Clareira das Ruínas (secreta)':'E'}
LC={'P':(70,140,230),'M':(120,110,100),'E':(60,170,80),'L':(160,110,60)}
MAIN=[[(640,1510),(640,1420)],[(640,1320),(640,1265)],[(600,995),(600,955)],[(600,855),(600,805)],[(560,635),(560,590)],[(560,490),(560,425)],[(560,275),(560,215)]]
SIDE=[[(190,600),(190,670)],[(190,770),(190,830)],[(340,430),(365,430),(365,350),(390,350)],[(730,300),(795,300)],[(905,350),(905,400)],
      [(740,720),(920,720),(920,600)],[(340,980),(380,980),(380,1100),(420,1100)],[(480,1265),(480,1310)],[(300,1410),(300,1485)]]
SECRET=[[(150,1030),(150,1080)],[(1000,600),(1000,805)],[(860,1215),(890,1215)],[(270,1360),(240,1360)],[(210,1675),(210,1740)],[(305,300),(390,300)]]
def road(pts,col,w):
    d.line(pts,fill=col,width=w,joint='curve')
    for t in(pts[0],pts[-1]):
        d.ellipse([t[0]-8,t[1]-8,t[0]+8,t[1]+8],fill=(250,250,240),outline=(20,20,20),width=3)
for p in SIDE:road(p,(170,140,96),12)
for p in SECRET:road(p,(90,170,165),9)
for p in MAIN:road(p,(255,206,70),18)
for n,(cx,cy,w,h,c,lv,k) in Z.items():
    r=[cx-w//2,cy-h//2,cx+w//2,cy+h//2]
    d.rounded_rectangle(r,radius=26 if k!=CA else 30,fill=c,outline=OUT[k],width=4)
    if k==CA:
        d.text((cx,r[1]+28),n,font=f(21 if len(n)<22 else 19),fill=(255,255,255),anchor='mm',stroke_width=3,stroke_fill=(15,15,15))
        d.text((cx,r[1]+58),lv,font=f(18),fill=(255,236,150),anchor='mm',stroke_width=3,stroke_fill=(15,15,15))
    else:
        nm=n.replace(' (secreta)','')
        d.text((cx+8,cy-13),nm,font=f(15),fill=(255,255,255),anchor='mm',stroke_width=3,stroke_fill=(15,15,15))
        d.text((cx+8,cy+13),lv+(' · secreta' if k==ES else ''),font=f(15),fill=(255,236,150),anchor='mm',stroke_width=3,stroke_fill=(15,15,15))
for nm_,tags in LS.items():
    cx,cy,w,h=Z[nm_][:4]
    for i,ch in enumerate(tags):
        x=cx+w//2-18-i*25;y=cy+h//2-16
        d.ellipse([x-10,y-10,x+10,y+10],fill=LC[ch],outline=(255,255,255),width=2);d.text((x,y),ch,font=f(12),fill=(255,255,255),anchor='mm')
d.ellipse([740,1190,830,1245],fill=(60,120,210),outline=(220,235,255),width=3)
def mk(x,y,kind,label=''):
    if kind=='camp':
        d.polygon([(x,y-14),(x-14,y+10),(x+14,y+10)],fill=(240,190,80),outline=(20,20,20));d.text((x,y+2),"!",font=f(15),fill=(40,20,0),anchor='mm')
    elif kind=='dg':
        d.polygon([(x,y-16),(x+16,y),(x,y+16),(x-16,y)],fill=(190,90,230),outline=(255,255,255),width=2)
    elif kind=='boss':
        d.ellipse([x-14,y-14,x+14,y+14],fill=(200,40,40),outline=(255,255,255),width=2);d.text((x,y),"☠",font=f(18),fill=(255,255,255),anchor='mm')
    elif kind=='poi':
        d.text((x,y),"★",font=f(22),fill=(120,230,255),anchor='mm',stroke_width=2,stroke_fill=(15,15,15))
    elif kind=='chest':
        d.rectangle([x-12,y-8,x+12,y+8],fill=(200,140,60),outline=(255,240,200),width=2);d.line([(x-12,y),(x+12,y)],fill=(255,240,200),width=2)
    if label:d.text((x+22,y),label,font=f(15),fill=(255,255,255),anchor='lm',stroke_width=3,stroke_fill=(15,15,15))
# zonas de caça
mk(500,1120,'camp','Acampamento');mk(790,1110,'camp')
mk(90,960,'camp');mk(260,985,'boss','Skrix');mk(100,1010,'boss','Grunk')
mk(90,520,'camp');mk(100,575,'boss','Gorgash')
mk(830,525,'camp');mk(850,580,'boss','Morvath');mk(1000,545,'dg','Cripta')
mk(90,1590,'camp');mk(110,1645,'boss','Rei dos Ratos');mk(290,1595,'dg','Esgotos')
mk(470,765,'camp');mk(650,770,'camp')
mk(470,395,'camp');mk(650,395,'camp')
# ligações: ponto de interesse; secretas: baú
mk(540-0,1370+0,'poi') if False else None
for (x,y) in [(535,1370),(210-110,720),(490,905),(440,540),(290,1360)]:
    pass
mk(535,1370,'poi');mk(98,720,'poi');mk(496,905,'poi');mk(458,540,'poi');mk(290,1360,'poi')
mk(75,1130,'chest');mk(850,860,'chest');mk(95,250,'chest');mk(905,1215,'chest');mk(60,1360,'chest');mk(110,1790,'chest');mk(817,300,'poi')
# aviso
d.text((640,1418),"sem NPCs: a cidade ainda está atrás",font=f(14,0),fill=(255,236,170),anchor='mm',stroke_width=3,stroke_fill=(15,15,15))
# legenda
y0=1960
d.rounded_rectangle([30,y0-40,W-30,H-24],radius=18,fill=(18,22,16),outline=(110,120,100),width=2)
rows=[("linha dourada = caminho principal",(255,206,70)),("linha marrom = caminho opcional",(170,140,96)),("linha verde-água = acesso a zona secreta",(90,170,165)),("círculo branco = saída da zona (fade)",(250,250,240))]
yy=y0-14
for t,c in rows:
    d.rectangle([50,yy-6,72,yy+6],fill=c);d.text((86,yy),t,font=f(16,0),fill=(235,235,225),anchor='lm');yy+=30
yy=y0+112
for t,c in [("zona de caça (borda branca)",OUT[CA]),("zona de ligação (borda areia)",OUT[LI]),("zona secreta (borda verde-água)",OUT[ES])]:
    d.rounded_rectangle([50,yy-9,72,yy+9],radius=5,outline=c,width=3);d.text((86,yy),t,font=f(16,0),fill=(235,235,225),anchor='lm');yy+=28
x0=620
yb=y0+205
d.text((50,yb),"vida (futuro, opcional):",font=f(15),fill=(235,235,225),anchor='lm')
for i,(ch,t) in enumerate([('P','pesca'),('M','mineração'),('E','ervas'),('L','lenha')]):
    x=300+i*115;d.ellipse([x-10,yb-10,x+10,yb+10],fill=LC[ch],outline=(255,255,255),width=2);d.text((x,yb),ch,font=f(12),fill=(255,255,255),anchor='mm');d.text((x+16,yb),t,font=f(14,0),fill=(235,235,225),anchor='lm')
mk(x0,y0-14,'camp','NPC avulso / quest');mk(x0,y0+18,'boss','Chefe de zona (ponto fixo)');mk(x0,y0+50,'dg','Entrada de dungeon (fechada)')
mk(x0,y0+82,'poi','Ponto de interesse (vista, ruína)');mk(x0,y0+114,'chest','Baú / hunt (futuro)')
d.text((W-50,H-48),"Teleporte só entre cidades",font=f(16),fill=(255,226,140),anchor='rm')
im.save('mundo_esboco3.png');print(im.size)
