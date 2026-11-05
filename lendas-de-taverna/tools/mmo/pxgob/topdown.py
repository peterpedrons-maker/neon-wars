"""Teste de estilo: goblin visto de cima/3-4 (como os mobs de referência): contorno na cor do próprio material, 4 tons, ombreiras e arma pendurada."""
import sys,math
from engine import *
from PIL import Image,ImageDraw
def goblin_td(P=None):
    P=P or {};g=Img(40,40);b=P.get('bob',0)
    def Y(y):return y+b
    # arma pendurada (atrás)
    g.shape(capsule((9.5,Y(23)),(9.5,Y(33)),.9,1.2),'D')
    g.shape(ellipse(9.5,Y(34.5),2.6,2.6),'D')
    for a in (0,72,144,216,288):
        r=math.radians(a+20);g.shape(poly([(9.5+math.cos(r)*2.2,Y(34.5)+math.sin(r)*2.2),(9.5+math.cos(r+.5)*2.6,Y(34.5)+math.sin(r+.5)*2.6),(9.5+math.cos(r+.2)*4.6,Y(34.5)+math.sin(r+.2)*4.6)]),'M',outline=False,flat=True)
    # pernas/pés
    g.shape(ellipse(16,Y(33.5),3.2,1.7),'O');g.shape(ellipse(24,Y(33.5),3.2,1.7),'O')
    # corpo e tanga
    g.shape(ellipse(20,Y(25),6.2,5.2),'O')
    g.shape(poly([(15,Y(27)),(25,Y(27)),(26,Y(30)),(23,Y(32)),(20,Y(30)),(17,Y(32)),(14,Y(30))]),'P')
    # braços abertos para baixo e mãos
    g.shape(capsule((13.5,Y(22)),(10.5,Y(28)),2.2,1.9),'O');g.shape(ellipse(10.5,Y(28.8),2.6,2.5),'H')
    g.shape(capsule((26.5,Y(22)),(29.5,Y(28)),2.2,1.9),'O');g.shape(ellipse(29.5,Y(28.8),2.6,2.5),'H')
    # ombreiras
    g.shape(ellipse(13,Y(21.3),4.2,2.7),'A');g.shape(ellipse(27,Y(21.3),4.2,2.7),'A')
    # orelhas horizontais
    g.shape(poly([(13,Y(13.5)),(2,Y(12)),(5,Y(16)),(13.5,Y(17))]),'O');g.shape(poly([(27,Y(13.5)),(38,Y(12)),(35,Y(16)),(26.5,Y(17))]),'O')
    # cabeça
    g.shape(ellipse(20,Y(15),7.6,6.6),'O',shade=.4)
    g.shape(ellipse(20,Y(10.4),2.6,1.6),'H',outline=False,flat=True)    # marca na testa
    # olhos
    for ex,col in((16.4,(214,52,40)),(23.6,(214,52,40))):
        g.dot(int(ex),int(Y(15.6)),(236,236,226));g.dot(int(ex+1),int(Y(15.6)),col);g.dot(int(ex+1),int(Y(16.6)),(40,30,28))
    g.dot(19,int(Y(18)),(100,112,52));g.dot(20,int(Y(18)),(100,112,52))
    for dx in range(-2,3):g.dot(20+dx,int(Y(20.2)),(52,64,34))
    g.dot(17,int(Y(20.2)),(250,246,220));g.dot(22,int(Y(20.2)),(250,246,220))
    return g
if __name__=='__main__':
    g=goblin_td();sp=g.render(12,None)
    bg=Image.new('RGBA',sp.size,(142,166,76,255));d=ImageDraw.Draw(bg);d.ellipse((60,360,420,450),fill=(112,128,64,255));bg.alpha_composite(sp);bg.convert('RGB').save(sys.argv[1]);print(bg.size)
