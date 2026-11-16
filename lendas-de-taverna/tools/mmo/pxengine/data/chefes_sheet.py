import sys; sys.path.insert(0, '.')
import chibi as C, creature as CRE, fauna as FA, export_atlas as X, pxfont
from PIL import Image, ImageDraw
OUTD = '/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel'
U = lambda **ap: dict(kind='c', ap=ap)
BOSS = {
 'morvath': U(cls='warrior', skin='osso', hair='azul', hairstyle='long', eyes='azul', hat='morvath', outfit='mail', clothes='azul', metal='aco', weapon='montante', tn_off=1, bulk=1, face_style='hollow'),
 'gorgash': U(cls='warrior', skin='ogro', hair='preto', hairstyle='mohawk', eyes='brasa', hat='gorgash', outfit='mail', clothes='bronze', metal='ferro', weapon='martelo_guerra', tn_off=2, bulk=1, face_style='brute'),
 'ratking': U(cls='rogue', skin='rato', hair='g_rato', hairstyle='spiky', eyes='vermelho', hat='ratking', outfit='cloth', clothes='roxo', weapon='adaga_sangue', weapon2='adaga_sangue', tn_off=1, face_style='sly'),
 'skrix': U(cls='mage', skin='goblin', hair='g_goblin', hairstyle='bald', eyes='amarelo', hat='skrix', outfit='robe', clothes='verde', weapon='cajado_caveira', tn_off=-1, face_style='fierce'),
 'boticario': U(cls='mage', skin='palida', hair='preto', hairstyle='long', eyes='verde', hat='boticario', outfit='robe', clothes='verde', weapon='cajado_natureza', face_style='cold'),
 'presa': U(cls='warrior', skin='javali', hair='g_javali', hairstyle='mane', eyes='brasa', hat='presa', outfit='mail', clothes='bronze', metal='ferro', weapon='machado', tn_off=2, bulk=1, face_style='brute'),
}
def spr(k, view):
    return X.frames(BOSS[k], 'idle', view)[0].convert('RGBA')
if __name__ == '__main__':
    names = list(BOSS); S = Image.new('RGBA', (70 * len(names), 176), (24, 18, 32, 255))
    for i, k in enumerate(names):
        c = Image.new('RGBA', (66, 156), (40, 30, 52, 255)); ImageDraw.Draw(c).rectangle([0, 0, 65, 155], outline=(120, 100, 60, 255))
        for view, yb in (('right', 50), ('down', 101), ('up', 152)):
            im = spr(k, view); b = im.getbbox(); c.alpha_composite(im.crop(b), (33 - (b[2] - b[0]) // 2, yb - (b[3] - b[1])))
        pxfont.text(c, (33, 1), k.upper(), (240, 226, 190), center=True); S.alpha_composite(c, (i * 70 + 2, 10))
    S.resize((S.width * 4, S.height * 4), Image.NEAREST).save(OUTD + '/chefes_novos.png'); print('ok')
