import json,subprocess,sys
D='/tmp/mt/trailer2/';T=json.load(open(D+'T.json'))
order=['a','b','c_guerreiro','c_ladino','c_mago','c_clerigo','c_arqueiro','c_bardo','d','e','f']
OUT=sys.argv[1];X=.35
import re,os
for n in T:
    if 'act' not in T[n]:
        r=subprocess.run(['ffmpeg','-i',T[n]['file'],'-f','null','-'],capture_output=True,text=True).stderr
        t=re.findall(r'time=(\d+):(\d+):([\d.]+)',r)[-1];T[n]['act']=int(t[0])*3600+int(t[1])*60+float(t[2])
json.dump(T,open(D+'T.json','w'))
subprocess.check_call(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i','sine=f=46:d=1.6','-f','lavfi','-i','anoisesrc=d=1.2:c=pink:a=.7','-filter_complex',
 '[0:a]afade=t=out:st=0.1:d=1.5,volume=2.6[a];[1:a]lowpass=f=520,afade=t=out:st=0:d=1.1,volume=1.4[b];[a][b]amix=inputs=2:normalize=0[o]','-map','[o]',D+'boom.wav'])
cmd=['ffmpeg','-y','-loglevel','error'];durs=[];evs=[]
for n in order:
    t=T[n];d=min(t['dur']-.12,t['act']-(t['ss']+.06)-.08);durs.append(d)
    cmd+=['-ss',f"{t['ss']+.06:.2f}",'-t',f'{d:.2f}','-i',t['file']]
cmd+=['-i','/home/user/neon-wars/lendas-de-taverna/assets/audio/music/chefe.ogg','-i',D+'boom.wav']
f=[]
for i,n in enumerate(order):
    d=durs[i]
    f.append(f"[{i}:v]fps=30,setsar=1,scale=w='trunc(1920*(1+0.07*t/{d:.2f})/2)*2':h='trunc(1080*(1+0.07*t/{d:.2f})/2)*2':eval=frame:flags=bicubic,crop=1920:1080,"
             f"eq=contrast=1.1:saturation=1.2:brightness=0.03:gamma=1.12,colorbalance=rs=-.03:bs=.05:rh=.05:bh=-.03,unsharp=5:5:.6,format=yuv420p[v{i}]")
cur='v0';acc=durs[0];starts=[0.0]
for i in range(1,len(order)):
    off=acc-X
    f.append(f'[{cur}][v{i}]xfade=transition={"fadeblack" if order[i] in ("b","d","f") else "fade"}:duration={X}:offset={off:.2f}[x{i}]');cur=f'x{i}';starts.append(off);acc=off+durs[i]
total=acc
f.append(f'[{cur}]fade=t=in:st=0:d=0.6,fade=t=out:st={total-1.4:.2f}:d=1.4[vout]')
# áudio: música + trovões nos textos
slams=[]
for i,n in enumerate(order):
    for lbl,tm in T[n]['ev']:
        slams.append((starts[i]+tm-.06,1.0 if not n.startswith('c_') else .55))
na=len(order);nb=na+1
parts=[f'[{na}:a]atrim=0:{total:.2f},afade=t=in:st=0:d=1.5,afade=t=out:st={total-3:.2f}:d=3,volume=.8[m]']
lab=['[m]']
for k,(tm,v) in enumerate(slams):
    parts.append(f'[{nb}:a]adelay={int(max(0,tm)*1000)}|{int(max(0,tm)*1000)},volume={v}[s{k}]');lab.append(f'[s{k}]')
parts.append(''.join(lab)+f'amix=inputs={len(lab)}:normalize=0:duration=first,alimiter=limit=.95[aout]')
f+=parts
cmd+=['-filter_complex',';'.join(f),'-map','[vout]','-map','[aout]','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',OUT]
subprocess.check_call(cmd);print('ok',round(total,1))
