"""Calibração v2: roda sim2.js nas 6 classes em 8 pontos de nível, tira a média e ajusta BAL.K em index.html (knots.py). Uso: python3 calib2.py <iterações> [minutos]"""
import subprocess,sys,json,re,statistics as st,os
from concurrent.futures import ThreadPoolExecutor
HERE=os.path.dirname(os.path.abspath(__file__));IDX=os.path.join(HERE,'..','..','..','mmo','index.html')
CLS=['guerreiro','ladino','mago','clerigo','arqueiro','bardo']
KN=[(1,1,'med'),(5,1,'med'),(10,2,'med'),(20,4,'med'),(30,6,'good'),(40,8,'bis'),(50,10,'bis'),(60,12,'bis')]
MIN=sys.argv[2] if len(sys.argv)>2 else '4'
def run(a):
    c,(L,z,k)=a
    for _ in range(2):
        r=subprocess.run(['node','/tmp/mt/sim2.cjs',c,MIN,str(L),str(z),k],capture_output=True,text=True,timeout=900,cwd='/tmp/mt')
        for ln in r.stdout.splitlines()[::-1]:
            if ln.startswith('{'):return json.loads(ln)
    return None
def getK():
    s=open(IDX).read();m=re.search(r'const BAL=\{zoneLv:5,K:(\{.*?\})\};',s);return json.loads(m.group(1))
def setK(K):
    s=open(IDX).read();txt=json.dumps(K,separators=(',',':'));s=re.sub(r'(const BAL=\{zoneLv:5,K:)\{.*?\}(\};)',lambda m:m.group(1)+txt+m.group(2),s,count=1);open(IDX,'w').write(s)
def dif(L):return min(1.0,max(0.0,(L-1)/59.0))**1.6
for it in range(int(sys.argv[1])):
    jobs=[(c,k) for k in KN for c in CLS]
    with ThreadPoolExecutor(4) as ex:res=list(ex.map(run,jobs))
    meas={};print('--- iteração',it+1)
    for k in KN:
        rs=[r for r in res if r and r['L']==k[0]];
        if not rs:continue
        loss=st.mean(r['loss'] for r in rs);cyc=st.mean(r['cycle'] for r in rs);d=sum(r['deaths'] for r in rs)
        meas[k[0]]=(loss,cyc);alvo=(.07+.30*dif(k[0]))*100;tt=5+8.5*dif(k[0])
        print('L%-3d z%-2d %-4s perda %5.1f%% (alvo %4.1f) ciclo %5.1fs (alvo %4.1f) mortes %d | por classe: %s'%(k[0],k[1],k[2],loss,alvo,cyc,tt,d,' '.join('%s:%.0f/%.0f'%(r['cls'][:3],r['loss'],r['cycle']) for r in rs)),flush=True)
    K=getK();out=subprocess.run(['python3',os.path.join(HERE,'knots.py'),json.dumps(meas),json.dumps(K),'0.8'],capture_output=True,text=True).stdout.strip()
    nk=json.loads(out);setK(nk);print('novo K',nk,flush=True)
