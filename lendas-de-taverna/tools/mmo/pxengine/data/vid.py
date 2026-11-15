"""Exporta lista de frames PIL para MP4 (ffmpeg): bem menor e mais suave que GIF, toca bem no celular."""
import os, subprocess, tempfile, shutil
from PIL import Image


def mp4(frames, path, fps=20, scale=1, loop=1):
    d = tempfile.mkdtemp(prefix='vid_')
    try:
        for i, f in enumerate(frames):
            im = f.convert('RGB')
            if scale != 1: im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
            if im.width % 2 or im.height % 2: im = im.crop((0, 0, im.width - im.width % 2, im.height - im.height % 2))
            im.save(os.path.join(d, '%05d.png' % i))
        seq = frames if loop == 1 else None
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(d, '%05d.png'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '12', '-preset', 'slow', '-movflags', '+faststart', path], check=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return os.path.getsize(path)
