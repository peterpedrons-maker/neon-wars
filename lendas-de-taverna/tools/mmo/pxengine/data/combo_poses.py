"""Ataques de combo REDESENHADOS por pose (guerreiro e ladino): cada golpe tem sua propria trajetoria de lamina, postura e pernas.
Convencao do angulo da arma (chibi.py): 0 = aponta para BAIXO, 90 = frente na horizontal, 180 = CIMA, 270 = para TRAS.
Cada ataque = 10 poses-chave (0-4 antecipacao, 5 o corte rapido, 6 IMPACTO, 7-9 recuperacao); 'attack(view, ap, nome)' devolve 20 quadros com o golpe no quadro 11."""
import math
import chibi as C
import chibi_anim2 as N2
W, H, BASE = C.W, C.H, C.BASE

def _hand(a, k=3):
    r = math.radians(a); return (round(k * math.sin(r)), round(k * math.cos(r)))

def _side(angs, lean, dy, tn, face, legs, sw2=None, arm_over=None, k=3, al_over=None, lute=False):
    P = []
    for i in range(10):
        hx, hy = _hand(angs[i], k)
        d = dict(tn=tn[i], dy=dy[i], hdx=lean[i], bdx=int(lean[i] * .6), dx=int(lean[i] * .7), ar=(hx + 1, hy), al=(0, 0), face=face[i],
                 sw=dict(kind='lute') if lute else dict(ang=angs[i], len=12))
        if al_over and al_over.get(i): d['al'] = al_over[i]
        if legs[i]: d['bl'], d['br'] = (-legs[i], 0), (legs[i], 0)
        if arm_over and arm_over.get(i): d['ar'] = arm_over[i]
        if sw2:
            a2 = sw2[i]; h2 = _hand(a2, 2)
            d['al'] = (round(h2[0] * .8), h2[1]); d['sw2'] = dict(ang=a2, len=8)
        P.append(d)
    return P

def _front(angs, lean, dy, tn, face, legs, sw2=None, arm_over=None, k=3, al_over=None, lute=False):
    P = []
    for i in range(10):
        hx, hy = _hand(angs[i], k)
        d = dict(tn=tn[i], dy=dy[i], hdy=-1 if lean[i] < -1 else (1 if lean[i] > 2 else 0), ar=(hx, hy), al=(0, 0), face=face[i], sw=dict(kind='lute') if lute else dict(ang=angs[i], len=12, side='r'))
        if al_over and al_over.get(i): d['al'] = al_over[i]
        if legs[i]: d['bl'], d['br'] = (-legs[i] // 2 - 1, 0), (legs[i] // 2 + 1, 0)
        if arm_over and arm_over.get(i): d['ar'] = arm_over[i]
        if sw2:
            a2 = sw2[i]; h2 = _hand(a2, 2); d['al'] = (h2[0], h2[1]); d['sw2'] = dict(ang=a2, len=8)
        P.append(d)
    return P

N, S_ = 'n', 'shout'
FACE = [N, N, N, N, N, S_, S_, S_, N, N]
# --------------------------------- GUERREIRO ---------------------------------
WAR = {
 # 1) CORTE DESCENDENTE: espada sobe por tras da cabeca e desce em diagonal
 'wchop': dict(angs=[150, 205, 268, 275, 278, 105, 50, 35, 60, 110], lean=[0, -1, -2, -3, -3, 2, 5, 5, 3, 1], dy=[0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
               tn=[3, 3, 3, 3, 3, 3, 2, 2, 3, 3], face=FACE, legs=[0, 0, 0, 1, 1, 2, 3, 3, 1, 0]),
 # 2) CORTE ASCENDENTE: abaixa a espada para tras agachado e sobe cortando de baixo para cima
 'wrise': dict(angs=[100, 70, 40, 15, 345, 25, 100, 160, 150, 120], lean=[0, 1, 2, 3, 3, 1, -2, -3, -2, 0], dy=[0, 0, 1, 1, 1, 0, 0, -1, 0, 0],
               tn=[3, 3, 2, 2, 2, 3, 3, 3, 3, 3], face=FACE, legs=[0, 1, 2, 3, 3, 3, 2, 1, 0, 0]),
 # 4) PANCADA COM SALTO: levanta a espada com as duas maos, salta e bate no chao
 'wslam': dict(angs=[120, 160, 172, 178, 178, 130, 20, 10, 40, 100], lean=[0, -1, -2, -2, -2, 2, 4, 4, 2, 0], dy=[0, 0, -1, -3, -4, -2, 2, 2, 1, 0],
               tn=[3, 3, 3, 3, 3, 3, 2, 2, 3, 3], face=FACE, legs=[0, 0, 0, 0, 0, 1, 3, 3, 1, 0], arm_over={3: (-1, -4), 4: (-1, -5), 5: (1, -2)}),
 # 5) GOLPE ESMAGADOR (skill empoderada): agacha fundo, ergue a espada com as duas maos, SALTA alto e esmaga o chao
 'wcrush': dict(angs=[110, 150, 178, 184, 184, 184, 12, 0, 20, 80], lean=[0, 1, -2, -3, -3, -3, 5, 6, 3, 0], dy=[1, 2, -1, -6, -9, -7, 2, 3, 1, 0],
               tn=[3, 2, 3, 3, 3, 3, 2, 2, 3, 3], face=FACE, legs=[0, 3, 1, 0, 0, 1, 3, 3, 1, 0], arm_over={2: (-1, -4), 3: (-1, -6), 4: (-1, -7), 5: (-1, -4), 6: (1, -1)}),
 # 6) ABALO SISMICO (skill empoderada): ergue a espada com as duas maos e a CRAVA no chao, ajoelhando; segura tremendo
 'wplant': dict(angs=[110, 150, 178, 184, 184, 120, 40, 4, 0, 0], lean=[0, -1, -2, -3, -3, 3, 6, 7, 7, 7], dy=[0, 0, -1, -3, -3, 0, 2, 3, 3, 3],
               tn=[3, 3, 3, 3, 3, 3, 2, 1, 1, 1], face=FACE, legs=[0, 0, 0, 0, 0, 1, 3, 3, 3, 3], arm_over={3: (-1, -5), 4: (-1, -5), 6: (1, 0), 7: (1, 2), 8: (1, 2), 9: (1, 2)}),
 # 7) MURALHA DE ESCUDOS (Cavaleiro empoderado): firma as pernas, crava a espada no chao a sua frente com as duas maos e se apoia nela, peito para frente
 'wwall': dict(angs=[110, 70, 30, 2, 0, 0, 0, 0, 40, 110], lean=[0, 1, 2, 3, 3, 3, 3, 3, 1, 0], dy=[0, 0, 1, 2, 2, 2, 2, 2, 1, 0],
               tn=[3, 3, 2, 2, 2, 2, 2, 2, 3, 3], face=[N, N, N, N, S_, S_, N, N, N, N], legs=[0, 1, 2, 3, 3, 3, 3, 3, 2, 0], arm_over={3: (1, 2), 4: (1, 2), 5: (1, 3), 6: (1, 3), 7: (1, 2)}),
 # 8) FURIA SELVAGEM (Barbaro empoderado): cabeca para tras, espada ao alto tremendo, pernas abertas, ruge
 'wrage': dict(angs=[110, 150, 178, 184, 184, 184, 184, 172, 140, 110], lean=[0, -1, -2, -3, -3, -3, -3, -2, -1, 0], dy=[0, 0, -1, -2, -2, -2, -2, -1, 0, 0],
               tn=[3, 3, 3, 3, 3, 3, 3, 3, 3, 3], face=[N, N, S_, S_, S_, S_, S_, S_, N, N], legs=[0, 1, 2, 3, 3, 3, 3, 2, 1, 0], arm_over={3: (-1, -6), 4: (-1, -7), 5: (-1, -7), 6: (-1, -7), 7: (-1, -5)}),
}
# --------------------------------- LADINO (duas adagas) ---------------------------------
ROG = {
 # 1) CORTE DIAGONAL com a adaga da frente (a de tras fica de guarda)
 'rcut': dict(angs=[120, 150, 170, 182, 185, 110, 50, 40, 60, 110], lean=[0, -1, -2, -2, -2, 2, 4, 4, 2, 0], dy=[0, 0, 0, 0, 0, 0, 1, 1, 0, 0], tn=[3, 3, 3, 3, 3, 3, 2, 2, 3, 3],
              face=FACE, legs=[0, 0, 1, 1, 1, 2, 2, 2, 1, 0], sw2=[120, 120, 125, 125, 125, 120, 115, 115, 120, 120]),
 # 2) CORTE INVERSO ASCENDENTE com a adaga de tras
 'rrev': dict(angs=[110, 110, 110, 110, 110, 100, 95, 100, 110, 110], lean=[0, 1, 2, 2, 2, 0, -2, -2, -1, 0], dy=[0, 0, 1, 1, 1, 0, 0, 0, 0, 0], tn=[3, 3, 2, 2, 2, 3, 3, 3, 3, 3],
              face=FACE, legs=[0, 1, 2, 2, 2, 2, 2, 1, 0, 0], sw2=[100, 60, 30, 10, 345, 40, 120, 165, 150, 120]),
 # 3) ESTOCADA DUPLA: recolhe as duas adagas e espeta uma depois da outra
 'rstab': dict(angs=[100, 95, 92, 90, 90, 88, 90, 90, 95, 100], lean=[0, -1, -2, -3, -3, 3, 5, 5, 3, 1], dy=[0, 0, 0, 0, 0, 0, 1, 1, 0, 0], tn=[3, 3, 3, 3, 3, 3, 2, 2, 3, 3],
               face=FACE, legs=[0, 0, 1, 1, 1, 3, 3, 3, 1, 0], sw2=[100, 98, 95, 92, 92, 90, 88, 88, 95, 100], arm_over={3: (-4, 0), 4: (-5, 0), 5: (6, 0), 6: (8, 0), 7: (8, 0)}),
 # 4) FINALIZADOR EM X: salta e cruza as duas adagas
 'rx': dict(angs=[140, 165, 180, 185, 185, 120, 55, 45, 60, 100], lean=[0, -1, -2, -2, -2, 2, 4, 4, 2, 0], dy=[0, 0, -1, -2, -3, -2, 1, 1, 0, 0], tn=[3, 3, 3, 3, 3, 3, 2, 2, 3, 3],
            face=FACE, legs=[0, 0, 0, 0, 0, 1, 3, 3, 1, 0], sw2=[100, 140, 170, 185, 190, 250, 305, 315, 300, 200]),
 # 5) CHUVA DE ADAGAS (skill): as duas maos sobem e arremessam as adagas para o alto
 'rrain': dict(angs=[110, 140, 170, 185, 185, 185, 175, 150, 120, 110], lean=[0, -1, -2, -3, -3, -3, -2, -1, 0, 0], dy=[0, 0, -1, -2, -2, -2, -1, 0, 0, 0], tn=[3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
               face=FACE, legs=[0, 1, 2, 2, 2, 2, 2, 1, 0, 0], sw2=[110, 135, 165, 185, 185, 185, 170, 145, 120, 110], arm_over={3: (-2, -6), 4: (-2, -7), 5: (-2, -7), 6: (-2, -5)}),
 # 6) EXECUCAO (skill): agacha fundo no escuro com as laminas baixas e some num bote para frente
 'rexec': dict(angs=[110, 80, 45, 20, 20, 20, 100, 90, 95, 110], lean=[0, 2, 3, 4, 4, 4, -1, -2, -1, 0], dy=[0, 1, 2, 3, 3, 3, 0, -1, 0, 0], tn=[3, 2, 2, 1, 1, 1, 3, 3, 3, 3],
               face=FACE, legs=[0, 1, 2, 3, 3, 3, 2, 1, 0, 0], sw2=[110, 85, 50, 25, 25, 25, 95, 88, 95, 110]),
 # 7) MARCA DA MORTE (skill do assassino): uma adaga aponta para o alvo e a outra risca o ar marcando-o
 'rmark': dict(angs=[110, 100, 95, 90, 90, 90, 90, 95, 100, 110], lean=[0, -1, -1, -2, -2, -2, -1, 0, 0, 0], dy=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], tn=[3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
               face=FACE, legs=[0, 1, 1, 2, 2, 2, 2, 1, 0, 0], sw2=[110, 150, 175, 175, 130, 70, 30, 60, 110, 110]),
 # 8) ARMADILHA DE ESPINHOS (skill do armadilheiro): agacha e crava as duas adagas no chao a sua frente
 'rtrap': dict(angs=[110, 70, 30, 5, 0, 0, 0, 0, 40, 110], lean=[0, 1, 2, 3, 3, 3, 3, 3, 1, 0], dy=[0, 1, 2, 3, 3, 3, 3, 3, 2, 0], tn=[3, 2, 2, 1, 1, 1, 1, 1, 2, 3],
               face=FACE, legs=[0, 1, 2, 3, 3, 3, 3, 3, 2, 0], sw2=[110, 75, 35, 8, 0, 0, 0, 0, 45, 110], arm_over={3: (1, 3), 4: (1, 3), 5: (1, 3), 6: (1, 3), 7: (1, 2)}),
}

# --------------------------------- MAGO (cajado) ---------------------------------
MAGE = {
 # 1) FOGO: recolhe o cajado ao peito e o estoca para frente soltando a bola
 'mthrust': dict(angs=[160, 140, 120, 105, 100, 88, 84, 88, 120, 160], lean=[0, -1, -2, -2, -2, 2, 3, 3, 1, 0], dy=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], tn=[3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                 face=FACE, legs=[0, 0, 1, 1, 1, 2, 2, 2, 1, 0], arm_over={3: (-2, -1), 4: (-3, -1), 5: (5, -1), 6: (6, -1)}),
 # 2) GELO: varre o cajado de baixo para cima num arco largo
 'msweep': dict(angs=[150, 110, 60, 20, 340, 20, 90, 150, 160, 150], lean=[0, 1, 2, 3, 3, 0, -2, -3, -2, 0], dy=[0, 0, 1, 1, 1, 0, 0, -1, 0, 0], tn=[3, 3, 2, 2, 2, 3, 3, 3, 3, 3],
                face=FACE, legs=[0, 1, 2, 3, 3, 3, 2, 1, 0, 0]),
 # 4) ARCANO: levita, ergue o cajado com as duas maos e o crava apontando para o alvo
 'mchan': dict(angs=[160, 172, 180, 182, 182, 160, 70, 50, 80, 130], lean=[0, 0, -1, -1, -1, 1, 3, 3, 1, 0], dy=[0, 0, -1, -2, -3, -3, -1, 0, 0, 0], tn=[3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
               face=FACE, legs=[0, 0, 0, 0, 0, 0, 2, 2, 1, 0], arm_over={2: (0, -4), 3: (0, -5), 4: (0, -6), 5: (0, -5), 6: (3, 0)}, al_over={2: (0, -4), 3: (0, -5), 4: (0, -6), 5: (0, -5), 6: (2, 1)}),
 # 5) METEOROS (skill): levita e ergue o cajado com as duas maos, tremendo, apontando para o ceu
 'msky': dict(angs=[150, 165, 180, 182, 178, 182, 178, 182, 170, 140], lean=[0, -1, -2, -3, -3, -3, -3, -3, -1, 0], dy=[0, -1, -2, -3, -4, -4, -4, -4, -2, 0], tn=[3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
              face=FACE, legs=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], arm_over={2: (0, -4), 3: (0, -6), 4: (0, -7), 5: (0, -7), 6: (0, -7), 7: (0, -6)}, al_over={2: (0, -4), 3: (0, -6), 4: (0, -7), 5: (0, -7), 6: (0, -7), 7: (0, -6)}),
 # 6) NOVA GELIDA (skill): agacha e bate o cajado no chao a frente; o gelo explode em volta
 'mfrost': dict(angs=[150, 175, 180, 150, 90, 20, 5, 0, 10, 60], lean=[0, -1, -2, 0, 3, 4, 4, 4, 2, 0], dy=[0, 0, -1, 0, 1, 3, 3, 3, 2, 0], tn=[3, 3, 3, 3, 2, 1, 1, 1, 2, 3],
               face=FACE, legs=[0, 0, 1, 1, 2, 3, 3, 3, 2, 0], arm_over={5: (3, 3), 6: (3, 3), 7: (3, 3)}, al_over={5: (3, 3), 6: (3, 3), 7: (3, 3)}),
 # 7) RAIO ARCANO (skill): firma as pernas e aponta o cajado reto para o alvo, segurando o raio
 'mbeam': dict(angs=[150, 120, 95, 90, 90, 90, 90, 90, 100, 130], lean=[0, 1, 2, 3, 3, 3, 3, 3, 1, 0], dy=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], tn=[3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
              face=FACE, legs=[0, 1, 2, 3, 3, 3, 3, 3, 2, 0], arm_over={3: (6, -2), 4: (7, -2), 5: (7, -2), 6: (7, -2), 7: (7, -2)}, al_over={3: (6, -2), 4: (7, -2), 5: (7, -2), 6: (7, -2), 7: (7, -2)}),
 # 8) INFERNO (skill do piromante): gira o cajado em arco baixo e aponta para o alvo, incendiando-o
 'mburn': dict(angs=[150, 120, 60, 20, 10, 40, 80, 95, 100, 130], lean=[0, 1, 2, 3, 3, 2, 2, 3, 1, 0], dy=[0, 0, 1, 1, 1, 0, 0, 0, 0, 0], tn=[3, 3, 2, 2, 2, 3, 3, 3, 3, 3],
              face=FACE, legs=[0, 1, 2, 3, 3, 3, 2, 2, 1, 0], arm_over={6: (6, -2), 7: (6, -2)}, al_over={6: (6, -2), 7: (6, -2)}),
 # 9) ESTACAS DE PEDRA (skill do geomante): bate o cajado duas vezes no chao
 'mrock': dict(angs=[150, 180, 150, 40, 5, 150, 40, 5, 20, 80], lean=[0, -2, -1, 3, 4, -1, 3, 4, 2, 0], dy=[0, -1, 0, 2, 3, 0, 2, 3, 2, 0], tn=[3, 3, 3, 2, 1, 3, 2, 1, 2, 3],
              face=FACE, legs=[0, 1, 1, 3, 3, 1, 3, 3, 2, 0], arm_over={4: (3, 3), 7: (3, 3)}, al_over={4: (3, 3), 7: (3, 3)}),
}
# --------------------------------- CLERIGO (maca) ---------------------------------
CLE = {
 # 1) MACETADA: sobe a maca em frente do rosto e desce pesada
 'cbash': dict(angs=[140, 165, 180, 185, 185, 95, 40, 25, 50, 110], lean=[0, -1, -2, -2, -2, 2, 4, 4, 2, 0], dy=[0, 0, 0, 0, 0, 0, 1, 1, 0, 0], tn=[3, 3, 3, 3, 3, 3, 2, 2, 3, 3],
               face=FACE, legs=[0, 0, 1, 1, 1, 2, 3, 3, 1, 0]),
 # 2) BACKHAND: balanca a maca de frente para tras, em arco baixo
 'cback': dict(angs=[110, 90, 70, 55, 50, 10, 325, 295, 285, 270], lean=[0, 1, 2, 3, 3, 1, -2, -3, -2, 0], dy=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], tn=[3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
               face=FACE, legs=[0, 1, 1, 2, 2, 3, 3, 2, 1, 0]),
 # 4) JULGAMENTO: levita em prece com a maca erguida e a desce sobre o alvo
 'cpray': dict(angs=[120, 160, 176, 180, 180, 178, 50, 10, 30, 100], lean=[0, 0, -1, -1, -1, 0, 3, 4, 2, 0], dy=[0, 0, -1, -2, -3, -3, 0, 1, 0, 0], tn=[3, 3, 3, 3, 3, 3, 2, 2, 3, 3],
               face=FACE, legs=[0, 0, 0, 0, 0, 0, 3, 3, 1, 0], arm_over={2: (0, -4), 3: (0, -5), 4: (0, -6), 5: (0, -6)}, al_over={2: (0, -4), 3: (0, -5), 4: (0, -6), 5: (0, -6)}),
}
# --------------------------------- BARDO (alaude) ---------------------------------
BARD = {
 'bstrum': dict(angs=[0] * 10, lean=[0, -1, -1, 1, 1, 2, -1, 2, 0, 0], dy=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], tn=[3, 3, 3, 3, 3, 3, 3, 3, 3, 3], face=[N, N, S_, S_, S_, S_, S_, S_, N, N],
                legs=[0, 1, 2, 1, 2, 2, 1, 1, 0, 0], arm_over={0: (0, 0), 1: (0, -3), 2: (0, 3), 3: (0, -4), 4: (0, 4), 5: (0, -4), 6: (0, 3), 7: (0, -2), 8: (0, 0), 9: (0, 0)}, lute=True),
 'bdance': dict(angs=[0] * 10, lean=[0, 1, 2, 1, -1, -2, -1, 1, 2, 0], dy=[0, -1, -2, 0, -1, -2, 0, -1, 0, 0], tn=[3, 3, 3, 3, 3, 3, 3, 3, 3, 3], face=[N, S_, S_, S_, S_, S_, S_, S_, N, N],
                legs=[0, 2, 0, 2, 0, 2, 0, 2, 0, 0], arm_over={1: (0, -2), 2: (0, -3), 3: (0, 2), 4: (0, -3), 5: (0, 2), 6: (0, -3), 7: (0, 2)}, lute=True),
 'bchord': dict(angs=[0] * 10, lean=[0, -1, -1, -1, -1, 0, 2, 3, 1, 0], dy=[0, 0, -1, -2, -3, -3, 1, 1, 0, 0], tn=[3, 3, 3, 3, 3, 3, 2, 2, 3, 3], face=[N, N, N, S_, S_, S_, S_, S_, N, N],
                legs=[0, 0, 0, 0, 0, 0, 3, 3, 1, 0], arm_over={2: (0, -5), 3: (0, -6), 4: (0, -6), 5: (0, -6), 6: (1, 4), 7: (1, 4), 8: (0, 1)}, al_over={2: (0, -5), 3: (0, -6), 4: (0, -6), 5: (0, -6), 6: (0, 4), 7: (0, 4)}, lute=True),
}
# --------------------------------- ARQUEIRO (arco) ---------------------------------
BOWD = {'right': (1, 0), 'down': (0, 1), 'up': (0, -1)}
def _bow(d, draw, arrow=True, mode='aim'): return dict(kind='bow', dir=d, draw=draw, arrow=arrow, mode=mode)
def _archer(view, name):
    d = BOWD[view]; B = lambda draw, a=True, m='aim': _bow(d, draw, a, m); f = 'shout'
    if name == 'aq2':     # tiro rapido: avanca um passo, puxa e solta de uma vez
        return [dict(sw=B(0, False, 'carry')), dict(sw=B(4), dx=1), dict(sw=B(8), dx=1, hdx=-1, tn=2, face=f), dict(sw=B(8), dx=1, hdx=-1, tn=2, face=f), dict(sw=B(8), dx=2, hdx=-1, tn=2, face=f),
                dict(sw=B(0, False), dx=2, hdx=1, bdx=1, br=(1, 0)), dict(sw=B(-1, False), dx=2, hdx=1), dict(sw=B(2, False), dx=1), dict(sw=B(0, False), dx=1), dict(sw=B(0, False, 'carry'))]
    if name == 'aq3':     # tiro duplo: solta, rearma e solta de novo, com pulinho de lado
        return [dict(sw=B(0, False, 'carry')), dict(sw=B(5)), dict(sw=B(8), hdx=-1, tn=2, face=f), dict(sw=B(8), hdx=-1, tn=2, face=f), dict(sw=B(0, False), hdx=1, dy=-1, br=(0, 1), bl=(0, 1)),
                dict(sw=B(8), hdx=-1, dy=-2, tn=2, face=f), dict(sw=B(0, False), hdx=1, dy=-1), dict(sw=B(-1, False), dy=0, hdx=1), dict(sw=B(2, False)), dict(sw=B(0, False, 'carry'))]
    if name == 'aq4':     # PULO PARA TRAS + TIRO CARREGADO: agacha, salta de costas, concentra no ar (arco todo puxado) e solta
        return [dict(sw=B(0, False, 'carry')), dict(sw=B(2), tn=2, dy=1, hdx=-1), dict(sw=B(4), dy=-2, dx=-2, hdx=-1, bl=(0, 2), br=(0, 2)), dict(sw=B(7), dy=-5, dx=-4, hdx=-2, bdx=-1, bl=(0, 3), br=(0, 3), face=f),
                dict(sw=B(9), dy=-7, dx=-5, hdx=-2, bdx=-1, bl=(0, 3), br=(0, 3), tn=2, face=f), dict(sw=B(10), dy=-7, dx=-5, hdx=-2, bdx=-1, bl=(0, 3), br=(0, 3), tn=2, face=f),
                dict(sw=B(0, False), dy=-6, dx=-5, hdx=2, bdx=1, bl=(0, 3), br=(0, 3), face=f), dict(sw=B(-1, False), dy=-3, dx=-5, hdx=1, bl=(0, 2), br=(0, 2)),
                dict(sw=B(2, False), dy=1, dx=-4, tn=2, hdx=1), dict(sw=B(0, False, 'carry'), dx=-3)]
    raise KeyError(name)
TABLE = dict(WAR, **ROG)
TABLE.update(MAGE); TABLE.update(CLE); TABLE.update(BARD)
ARCH = ('aq2', 'aq3', 'aq4')
for _n in ARCH: TABLE[_n] = None
# opcoes por ataque: seq (indices dos quadros densos), poeira/clarao
OPT = {
 'aq4': dict(seq=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 12, 13, 14, 14, 15, 16, 17, 18], flash=12, dust=[(16, .3), (17, .6), (18, .85)], heavy=True),
 'mchan': dict(heavy=True), 'mfrost': dict(heavy=True), 'mrock': dict(heavy=True), 'cpray': dict(heavy=True), 'bchord': dict(heavy=True),
}

SEQ = [0, 1, 2, 3, 4, 5, 6, 7, 8, 8, 9, 10, 12, 13, 13, 14, 15, 16, 17, 18]          # indices dos 19 quadros densos; o golpe cai no 11-12

def poses(view, name):
    if name in ARCH: return _archer(view, name)
    t = TABLE[name]
    return (_side if view == 'right' else _front)(t['angs'], t['lean'], t['dy'], t['tn'], t['face'], t['legs'], t.get('sw2'), t.get('arm_over'), 3, t.get('al_over'), t.get('lute', False))

def attack(view, ap, name):
    cls = ap.get('cls', 'warrior')
    base = C.anim(view, 'attack', cls, C.densify(poses(view, name), 2), ap, dense=2)
    fr = [b[0] for b in base]; out = []
    o = OPT.get(name, {}); heavy = o.get('heavy', name in ('wslam', 'rx', 'wcrush', 'wplant', 'wwall', 'rtrap', 'rrain')); seq = o.get('seq', SEQ)
    for k, i in enumerate(seq):
        im = fr[min(i, len(fr) - 1)]
        if k == o.get('flash', 11): im = N2.flash(im, .35 if heavy else .22)
        if 'dust' in o:
            for kk, st in o['dust']:
                if k == kk: im = N2.dust(im, st, cx=W // 2 + 2, n=6)
        elif k in (11, 12) and not heavy: im = N2.shake(im, 1, 0)
        elif heavy and name not in ('aq4',):
            if k == 11: im = N2.shake(im, 1, 1)
            if k in (11, 12): im = N2.dust(im, .12 + .22 * (k - 11), cx=W // 2 + 6, n=6)
            if k == 13: im = N2.dust(im, .55, cx=W // 2 + 6, n=6)
            if k == 14: im = N2.dust(im, .8, cx=W // 2 + 6, n=5)
        out.append(im)
    return out


# ---------------------------------------------------------------- TUFAO (Giro de Lamina empoderado): loop de giro com a espada nas DUAS maos
TW_FACE = ['down', 'down', 'right', 'right', 'up', 'up', 'left', 'left']
TW_ANG = {'down': (65, 110), 'right': (80, 100), 'up': (90, 90), 'left': (80, 100)}

def _twirl_pose(view, k, i):
    """k = 0..7 (passo da volta), i = quadro (0..15) para alternar pernas/quique. Espada esticada na horizontal, as duas maos no cabo."""
    sub = k % 2; a = TW_ANG[TW_FACE[k]][sub]
    hx, hy = _hand(a, 3)
    hop = 1 if (i % 2 == 0) else 0
    p = dict(tn=2 if hop else 3, dy=-1 if hop else 0, face='shout', hdx=0, ar=(hx, hy), al=(hx - 1, hy), nomitt=False)
    p['bl'], p['br'] = ((-2, 0), (2, 0)) if hop else ((-1, 0), (1, 0))
    if view == 'right':
        p['sw'] = dict(ang=a, len=13); p['hdx'] = 1; p['bdx'] = 1; p['ar'] = (hx + 1, hy)
    else:
        p['sw'] = dict(ang=a, len=13, side='r'); p['hdy'] = 0
    return p

def twirl(ap, n=16):
    """n quadros do giro: o heroi roda frente -> lado -> costas -> lado (espelhado), duas voltas; independe da vista pedida."""
    from PIL import ImageOps
    cls = ap.get('cls', 'warrior'); out = []
    for i in range(n):
        k = i % 8; fv = TW_FACE[k]; view = 'right' if fv == 'left' else fv
        p = _twirl_pose(view, k, i)
        im = C.anim(view, 'attack', cls, [p], ap, dense=1)[0][0].convert('RGBA')
        if fv == 'left' or (fv == 'up' and k % 2 == 1): im = ImageOps.mirror(im)
        if i % 4 == 1: im = N2.dust(im, .35, cx=W // 2, n=4)
        out.append(im)
    return out
