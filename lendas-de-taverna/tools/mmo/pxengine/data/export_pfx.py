"""Exporta um efeito do PixelFx para uma folha do jogo: mmo/assets/fx/<nome>.png/.json (+ prévia GIF opcional).
Uso: python3 export_pfx.py <cat/efeito> <nome> <t0> <t1> [fps=20] [opts-json] [--loop]
  t0..t1 em segundos recortam o trecho util. Origem (ox,oy) = pivo do efeito (chao) dentro do quadro recortado.
Requer o checkout do PixelFx em /root/pixelfx (node tools/render.mjs)."""
import json, subprocess, sys, os, tempfile
from PIL import Image
PFX = os.environ.get('PFX_DIR', '/root/pixelfx'); OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../mmo/assets/fx')
def run(fid, name, t0, t1, fps=20, opts=None, prev=None):
    tmp = tempfile.mkdtemp()
    cmd = ['node', 'tools/render.mjs', fid, '--sheet', '--fps', str(fps), '--no-actor', '--out', tmp]
    if opts: cmd += ['--opts', opts]
    subprocess.run(cmd, cwd=PFX, check=True, capture_output=True)
    d = os.path.join(tmp, fid) + '/'; base = fid.split('/')[1]
    j = json.load(open(d + base + '.json')); im = Image.open(d + base + '.png').convert('RGBA')
    fw, fh = j['meta']['pixelfx']['frameSize']; piv = j['meta']['pixelfx']['pivot']
    a, b = int(t0 * fps), min(len(j['frames']), int(t1 * fps) + 1)
    fs = [im.crop((f['frame']['x'], f['frame']['y'], f['frame']['x'] + fw, f['frame']['y'] + fh)) for f in j['frames'][a:b]]
    bb = None
    for f in fs:
        q = f.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
        if q: bb = q if bb is None else (min(bb[0], q[0]), min(bb[1], q[1]), max(bb[2], q[2]), max(bb[3], q[3]))
    w, h = bb[2] - bb[0], bb[3] - bb[1]; cols = 8
    sh = Image.new('RGBA', (w * cols, h * ((len(fs) + cols - 1) // cols)), (0, 0, 0, 0))
    for i, f in enumerate(fs): sh.paste(f.crop(bb), ((i % cols) * w, (i // cols) * h))
    os.makedirs(OUT, exist_ok=True)
    sh.save(f'{OUT}/{name}.png', optimize=True)
    json.dump(dict(w=w, h=h, n=len(fs), cols=cols, fps=fps, ox=piv[0] - bb[0], oy=piv[1] - bb[1]), open(f'{OUT}/{name}.json', 'w'))
    if prev:
        fr = []
        for f in fs:
            bg = Image.new('RGBA', (w, h), (22, 18, 34, 255)); bg.alpha_composite(f.crop(bb)); fr.append(bg.resize((w * 2, h * 2), Image.NEAREST).convert('P', palette=Image.ADAPTIVE, colors=96))
        fr[0].save(prev, save_all=True, append_images=fr[1:], duration=int(1000 / fps), loop=0, disposal=2)
    print(name, len(fs), 'quadros', w, 'x', h, os.path.getsize(f'{OUT}/{name}.png') // 1024, 'KB')
if __name__ == '__main__':
    a = sys.argv[1:]
    run(a[0], a[1], float(a[2]), float(a[3]), int(a[4]) if len(a) > 4 else 20, a[5] if len(a) > 5 else None)
