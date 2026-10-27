# Simulação do endgame: heróis por nível + kit de itens por tier/raridade (ver ITENS.md).
# Rodar: python3 tools/sim_endgame.py   (números da proposta, não do jogo)
import math
AT=['forca','destreza','constituicao','inteligencia','sabedoria','carisma']
BASE={'guerreiro':[14,10,13,8,9,9],'ladino':[9,14,11,11,10,10],'mago':[8,10,10,14,12,10],'clerigo':[11,9,12,10,14,11],'arqueiro':[9,14,11,10,11,9],'bardo':[8,12,10,11,10,14]}
GROW={'guerreiro':dict(forca=.5,constituicao=.3,destreza=.2),'ladino':dict(destreza=.5,constituicao=.2,inteligencia=.15,forca=.15),'mago':dict(inteligencia=.5,constituicao=.2,sabedoria=.2,destreza=.1),
'clerigo':dict(sabedoria=.45,constituicao=.25,forca=.2,carisma=.1),'arqueiro':dict(destreza=.55,constituicao=.2,sabedoria=.15,forca=.1),'bardo':dict(carisma=.45,destreza=.25,constituicao=.15,inteligencia=.15)}
AFIN={'guerreiro':['constituicao','forca'],'ladino':['destreza','constituicao'],'mago':['inteligencia','sabedoria'],'clerigo':['sabedoria','constituicao'],'arqueiro':['destreza','constituicao'],'bardo':['carisma','destreza']}
CLS={'guerreiro':dict(hp=28,atk=4,df=15,dmg=(1,8,2),atkA='forca',main='forca',sec='constituicao'),
'ladino':dict(hp=19,atk=5,df=13,dmg=(1,6,3),atkA='destreza',main='destreza',sec='constituicao'),
'mago':dict(hp=14,atk=5,df=11,dmg=(2,6,1),atkA='inteligencia',main='inteligencia',sec='sabedoria'),
'clerigo':dict(hp=21,atk=2,df=14,dmg=(1,6,1),atkA='forca',main='sabedoria',sec='constituicao'),
'arqueiro':dict(hp=17,atk=4,df=12,dmg=(1,8,1),atkA='destreza',main='destreza',sec='constituicao'),
'bardo':dict(hp=17,atk=2,df=12,dmg=(1,4,1),atkA='carisma',main='carisma',sec='destreza')}
def asg(x):return x-10 if x>=10 else -((10-x)//2)
def abv(x,d):return (x-10)//d if x>=10 else -((10-x)//(2*d))
def eff(a,A):
    return dict(atk=abv(a[A],8),dmg=asg(a[A])//2,hp=asg(a['forca'])+2*asg(a['constituicao']),df=abv(a['destreza'],8),dm=abv(a['constituicao'],8)+abv(a['sabedoria'],6),crit=max(0,abv(a['inteligencia'],8)),heal=max(0,asg(a['sabedoria'])//2))
def lvlpts(l):return 2 if l<=30 else 1
def hero(c,L):
    a=dict(zip(AT,BASE[c]));w=dict(GROW[c])
    for x in AFIN[c]:w[x]=w.get(x,0)+.2
    t=sum(w.values())
    pts=sum(lvlpts(l) for l in range(2,L+1))
    for k in w:a[k]+=int(pts*w[k]/t+1e-9)
    return a
RF=[.6,.8,1,1.25,1.5]
def kit(c,tier,rar):
    rf=RF[rar-1];cl=CLS[c];m=cl['main'];s=cl['sec']
    n=[2,2,3,3,4][rar-1]
    attr=lambda:max(1,round((1+0.35*(tier-1))*rf));dmg=lambda:max(1,round(0.4*tier*rf));atk=lambda:max(0,round(tier/6*rf));df=lambda:max(0,round(tier/8*rf));pv=lambda:max(1,round(1.2*tier*rf));rm=lambda:max(0,round(tier/8*rf))
    tot=dict(forca=0,destreza=0,constituicao=0,inteligencia=0,sabedoria=0,carisma=0,atk=0,dmg=0,df=0,pv=0,dm=0,crit=0)
    def add(lines,order):
        for ln in order[:n]:
            k=ln
            if k in AT:tot[k]+=attr()
            elif k=='dmg':tot['dmg']+=dmg()
            elif k=='atk':tot['atk']+=atk()
            elif k=='df':tot['df']+=df()
            elif k=='pv':tot['pv']+=pv()
            elif k=='dm':tot['dm']+=rm()
            elif k=='crit':tot['crit']+=1 if (tier>=6 and rar>=4) else 0
    two=c in('mago','arqueiro','bardo')
    add(0,[m,'dmg','atk','crit'])                       # arma
    add(0,[s,'df','pv','dm'] if c in('guerreiro','clerigo') else [m,'pv','dm','df'])  # corpo
    add(0,[s,'pv','df','atk'])                          # cabeça
    add(0,[m,'atk','dmg','df'])                         # mãos
    add(0,[s if c!='mago' else 'destreza','df','pv','dm'])  # pés
    if not two:add(0,[s,'df','pv','dm'] if c in('guerreiro','clerigo') else [m,'atk','dmg','crit'])  # mão secundária
    add(0,[m,s,'pv','df']);add(0,[s,m,'pv','dm'])       # acessórios
    return tot
def sheet(c,L,tier,rar):
    a=hero(c,L);cl=CLS[c];k=kit(c,tier,rar)
    for x in AT:a[x]+=k[x]
    e=eff(a,cl['atkA']);n,sd,b=cl['dmg']
    pv=cl['hp']+e['hp']+k['pv'];atk=cl['atk']+e['atk']+k['atk'];df=cl['df']+e['df']+k['df'];dm=round(cl['df']*.7)+e['dm']+k['dm']
    dmgb=b+e['dmg']+k['dmg'];avg=n*(sd+1)/2+dmgb;crit=min(6,e['crit']+k['crit'])
    return dict(pv=pv,atk=atk,df=df,dm=dm,dado=f'{n}d{sd}+{dmgb}',avg=avg,crit=crit,heal=e['heal'],attrs=[a[x] for x in AT])
for (L,tier,rar,label) in ((25,5,3,'Nv25 · tier 5 · Mágico (fim da 1ª passagem)'),(50,10,4,'Nv50 · tier 10 · Épico (fim da 2ª passagem)'),(60,12,5,'Nv60 · tier 12 · Lendário (endgame)')):
    print(label)
    for c in CLS:
        s=sheet(c,L,tier,rar)
        print(f"  {c:9s} PV {s['pv']:4d} ATQ {s['atk']:3d} DEF {s['df']:3d} ResMag {s['dm']:3d} dano {s['dado']:8s} (~{s['avg']:.0f}) crit {s['crit']} cura+{s['heal']}  attrs {s['attrs']}")

print()
print('Confronto: heroi vs inimigo comum do mesmo nivel (DEF do inimigo = base + nivel/5, hipotese)')
EN={25:dict(hp=68,atk=5,df=12,dmg=(1,6,11)),50:dict(hp=106,atk=7,df=13,dmg=(1,6,18)),60:dict(hp=125,atk=8,df=14,dmg=(1,6,22))}
for (L,tier,rar) in ((25,5,3),(50,10,4),(60,12,5)):
    e=EN[L];edf=e['df']+L//5;edm=e['dmg'][0]*(e['dmg'][1]+1)/2+e['dmg'][2]
    print(f'Nv{L}: inimigo PV {e["hp"]} DEF {edf} dano medio {edm:.0f}')
    for c in CLS:
        s_=sheet(c,L,tier,rar);p=min(.95,max(.05,(21-(edf-s_['atk']))/20))
        dpt=p*s_['avg']*(1+min(.5,.05+.05*s_['crit']));ph=min(.95,max(.05,(21-(s_['df']-e['atk']))/20))
        print(f"   {c:9s} acerta {p*100:3.0f}%  dano/turno {dpt:5.1f}  turnos p/ matar 1 inimigo {e['hp']/dpt:4.1f}   inimigo acerta {ph*100:3.0f}%  dano/turno no heroi {ph*edm:4.1f} ({s_['pv']/(ph*edm):4.0f} turnos p/ cair)")
