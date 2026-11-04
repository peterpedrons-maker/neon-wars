import json,subprocess,sys,os
D='/tmp/mt/trailer3/';T=json.load(open(D+'T.json'))
order=['a','b','c_guerreiro','c_ladino','c_mago','c_clerigo','c_arqueiro','c_bardo','d','e','f']
OUT=sys.argv[1];X=.35;FPS=60
# 1) cada cena: sequência de quadros com tempos reais -> mp4 em 60 fps constantes
for n in order:
    t=T[n];fr=t['frames'];ss,end=t['ss']+.06,t['end']-.06
    sel=[];prev=None
    for ts,f in fr:
        if ts<ss: prev=(ts,f);continue
        if ts>end: break
        sel.append((ts,f))
    if prev and (not sel or sel[0][0]>ss): sel.insert(0,(ss,prev[1]))
    lines=[]
    for i,(ts,f) in enumerate(sel):
        nxt=sel[i+1][0] if i+1<len(sel) else end
        lines.append(f"file '{f}'\nduration {max(.001,nxt-max(ts,ss)):.4f}")
    lines.append(f"file '{sel[-1][1]}'")
    open(D+f'l_{n}.txt','w').write('\n'.join(lines))
    subprocess.check_call(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',D+f'l_{n}.txt','-vf',f'fps={FPS},format=yuv420p','-c:v','libx264','-crf','14','-preset','veryfast',D+f'c_{n}.mp4'])
    t['clip']=D+f'c_{n}.mp4';t['cd']=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',t['clip']]).strip())
    print(n,len(sel),round(t['cd'],2))
subprocess.check_call(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i','sine=f=46:d=1.6','-f','lavfi','-i','anoisesrc=d=1.2:c=pink:a=.7','-filter_complex',
 '[0:a]afade=t=out:st=0.1:d=1.5,volume=2.6[a];[1:a]lowpass=f=520,afade=t=out:st=0:d=1.1,volume=1.4[b];[a][b]amix=inputs=2:normalize=0[o]','-map','[o]',D+'boom.wav'])
cmd=['ffmpeg','-y','-loglevel','error'];durs=[]
for n in order:
    t=T[n];d=t['cd']-.05;durs.append(d);cmd+=['-t',f'{d:.3f}','-i',t['clip']]
cmd+=['-i','/home/user/neon-wars/lendas-de-taverna/assets/audio/music/chefe.ogg','-i',D+'boom.wav']
f=[]
for i,n in enumerate(order):
    d=durs[i]
    f.append(f"[{i}:v]setsar=1,scale=w='trunc(1080*(1+0.06*t/{d:.2f})/2)*2':h='trunc(1920*(1+0.06*t/{d:.2f})/2)*2':eval=frame:flags=bicubic,crop=1080:1920,"
             f"eq=contrast=1.1:saturation=1.2:brightness=0.03:gamma=1.12,colorbalance=rs=-.03:bs=.05:rh=.05:bh=-.03,unsharp=5:5:.5,format=yuv420p[v{i}]")
cur='v0';acc=durs[0];starts=[0.0]
for i in range(1,len(order)):
    off=acc-X
    f.append(f'[{cur}][v{i}]xfade=transition={"fadeblack" if order[i] in ("b","d","f") else "fade"}:duration={X}:offset={off:.3f}[x{i}]');cur=f'x{i}';starts.append(off);acc=off+durs[i]
total=acc
f.append(f'[{cur}]fade=t=in:st=0:d=0.6,fade=t=out:st={total-1.4:.2f}:d=1.4[vout]')
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
cmd+=['-filter_complex',';'.join(f),'-map','[vout]','-map','[aout]','-r',str(FPS),'-c:v','libx264','-crf','21','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',OUT]
subprocess.check_call(cmd);print('ok',round(total,1))
