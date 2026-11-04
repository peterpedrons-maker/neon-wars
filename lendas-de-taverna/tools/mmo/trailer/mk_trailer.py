import json,subprocess,sys
D='/tmp/mt/trailer/';T=json.load(open(D+'T.json'))
order=['a','b','c','d','e','f','g'];X=.55
OUT=sys.argv[1]
cmd=['ffmpeg','-y','-loglevel','error']
durs=[]
for n in order:
    t=T[n];d=t['dur']-.15;durs.append(d)
    cmd+=['-ss',f"{t['ss']+.1:.2f}",'-t',f'{d:.2f}','-i',t['file']]
cmd+=['-i','/home/user/neon-wars/lendas-de-taverna/assets/audio/music/chefe.ogg']
f=[]
for i in range(len(order)):
    f.append(f'[{i}:v]fps=30,crop=390:844:0:0,scale=780:1688:flags=bicubic,setsar=1,vignette=PI/5,eq=contrast=1.1:saturation=1.2:brightness=-0.02,format=yuv420p[v{i}]')
cur='v0';acc=durs[0]
for i in range(1,len(order)):
    off=acc-X
    f.append(f'[{cur}][v{i}]xfade=transition=fadeblack:duration={X}:offset={off:.2f}[x{i}]');cur=f'x{i}';acc=off+durs[i]
total=acc
f.append(f'[{cur}]fade=t=in:st=0:d=0.5,fade=t=out:st={total-1.2:.2f}:d=1.2[vout]')
f.append(f'[{len(order)}:a]atrim=0:{total:.2f},afade=t=in:st=0:d=1.2,afade=t=out:st={total-2.5:.2f}:d=2.5,volume=.9[aout]')
cmd+=['-filter_complex',';'.join(f),'-map','[vout]','-map','[aout]','-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',OUT]
subprocess.check_call(cmd);print('ok',round(total,1))
