import sys,math
from engine2 import *
from PIL import Image,ImageDraw
def goblin_td(P=None):
    P=P or {};g=Img(44,44);b=P.get('bob',0)
    def Y(y):return y+b
    # sombra no chão fica fora do sprite (desenhada na composição)
    # arma pendurada à esquerda
    g.shape(tube((9.5,Y(24)),(9.8,Y(34)),1.1,1.5),'D')
    for k,(dx,dy) in enumerate(((0,0),)):pass
    g.shape(ellipsoid(10,Y(36.3),3.3,3.2),'D',dither=.05)
    for a in (10,82,154,226,298):
        r=math.radians(a);cx,cy=10+math.cos(r)*3.0,Y(36.3)+math.sin(r)*3.0;ex,ey=10+math.cos(r)*6.2,Y(36.3)+math.sin(r)*6.2
        nx,ny=-math.sin(r)*.9,math.cos(r)*.9
        g.shape(bevel([(cx+nx,cy+ny),(cx-nx,cy-ny),(ex,ey)],1.0),'M',outline=False)
    # pés
    g.shape(ellipsoid(17,Y(36),3.6,2.0),'O');g.shape(ellipsoid(27,Y(36),3.6,2.0),'O')
    for fx in(15.2,17,18.8,25.2,27,28.8):g.dot(int(fx),int(Y(37.6)),RAMPS['W'][2])
    # corpo e tanga
    g.shape(ellipsoid(22,Y(27.5),7.2,6.0),'O')
    g.shape(bevel([(16.5,Y(29.5)),(27.5,Y(29.5)),(28.5,Y(33)),(25,Y(35)),(22,Y(32.6)),(19,Y(35)),(15.5,Y(33))],2.0),'P',dither=.04)
    g.shape(tube((17,Y(26.6)),(27,Y(26.6)),.8,.8),'D',outline=False)
    g.dot(21,int(Y(26.2)),RAMPS['M'][1]);g.dot(22,int(Y(26.2)),RAMPS['M'][1]);g.dot(21,int(Y(27)),RAMPS['M'][3]);g.dot(22,int(Y(27)),RAMPS['M'][3])
    # braços e mãos
    g.shape(tube((15,Y(24)),(11.5,Y(30.5)),2.5,2.1),'O');g.shape(ellipsoid(11.3,Y(31.2),2.9,2.7),'H')
    g.shape(tube((29,Y(24)),(32.5,Y(30.5)),2.5,2.1),'O');g.shape(ellipsoid(32.7,Y(31.2),2.9,2.7),'H')
    for ex in(10.2,12.4,31.6,33.8):g.dot(int(ex),int(Y(32.4)),RAMPS['H'][4])
    # ombreiras
    g.shape(ellipsoid(14,Y(23.2),4.6,3.0),'A',dither=.04);g.shape(ellipsoid(30,Y(23.2),4.6,3.0),'A',dither=.04)
    g.shape(tube((11.8,Y(22.4)),(16,Y(22.4)),.5,.5),'M',outline=False);g.shape(tube((28,Y(22.4)),(32.2,Y(22.4)),.5,.5),'M',outline=False)
    # orelhas
    g.shape(bevel([(14.5,Y(14.2)),(2,Y(11.5)),(3.5,Y(16.8)),(8,Y(18.2)),(14.8,Y(18.6))],2.0),'O')
    g.shape(bevel([(29.5,Y(14.2)),(42,Y(11.5)),(40.5,Y(16.8)),(36,Y(18.2)),(29.2,Y(18.6))],2.0),'O')
    g.shape(bevel([(13,Y(14.8)),(5.5,Y(13.4)),(6.5,Y(16.4)),(13,Y(17.4))],1.2),'H',outline=False,bias=-.1)
    g.shape(bevel([(31,Y(14.8)),(38.5,Y(13.4)),(37.5,Y(16.4)),(31,Y(17.4))],1.2),'H',outline=False,bias=-.1)
    # cabeça
    g.shape(ellipsoid(22,Y(16),8.3,7.1),'O',dither=.03)
    g.shape(ellipsoid(22,Y(10.6),3.0,1.7),'H',outline=False,flat=1)         # marca dourada
    g.shape(ellipsoid(22,Y(19.4),3.2,2.4),'O',outline=False,bias=.05)       # focinho
    # sobrancelhas pesadas
    for sx in(-1,1):
        g.shape(tube((22+sx*2.4,Y(14.3)),(22+sx*6.4,Y(15.6) if sx>0 else Y(15.6)),.9,.7),'O',outline=False,bias=-.3)
    # olhos
    for sx in(-1,1):
        ex=int(22+sx*4.2-1)
        g.dot(ex,int(Y(16.4)),RAMPS['W'][0]);g.dot(ex+1,int(Y(16.4)),RAMPS['E'][1]);g.dot(ex+1,int(Y(17.4)),RAMPS['O'][4]);g.dot(ex,int(Y(17.4)),RAMPS['O'][4])
    g.dot(21,int(Y(19)),RAMPS['O'][4]);g.dot(22,int(Y(19)),RAMPS['O'][4])
    for dx in range(-3,3):g.dot(22+dx,int(Y(21.3)),RAMPS['O'][4])
    g.dot(19,int(Y(20.4)),RAMPS['W'][0]);g.dot(25,int(Y(20.4)),RAMPS['W'][0]);g.dot(19,int(Y(21.3)),RAMPS['W'][1]);g.dot(25,int(Y(21.3)),RAMPS['W'][1])
    return g.finish()
if __name__=='__main__':
    g=goblin_td();sp=g.render(12,None)
    bg=Image.new('RGBA',sp.size,(142,166,76,255));d=ImageDraw.Draw(bg);d.ellipse((60,400,470,490),fill=(112,128,64,255));bg.alpha_composite(sp);bg.convert('RGB').save(sys.argv[1]);print(bg.size)
