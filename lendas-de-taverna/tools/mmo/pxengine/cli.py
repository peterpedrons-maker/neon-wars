"""Linha de comando: python -m pxengine.cli build [personagem] [--out pasta]  |  preview <anim> [--window]  |  fx"""
import sys,os,argparse
from .character import Character
from .export import render_anim,export
from .validate import validate,report
from .preview import gifs,contact,window
from .animation import TEMPLATES
from . import effects
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'data')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('cmd',choices=['build','preview','fx']);ap.add_argument('--char',default='goblin');ap.add_argument('--anim',default='walk');ap.add_argument('--out',default='out');ap.add_argument('--window',action='store_true');a=ap.parse_args()
    if a.cmd=='fx':effects.export_fx(os.path.join(a.out,'fx'));print('efeitos em',a.out);return
    ch=Character(os.path.join(D,a.char+'.json'))
    if a.cmd=='build':
        anims=[render_anim(ch,n) for n in TEMPLATES];export(ch,anims,a.out);iss=validate(ch,anims);print(report(iss))
        for A in anims:gifs(ch,A,os.path.join(a.out,'preview'));contact(ch,A,os.path.join(a.out,'preview'))
    else:
        A=render_anim(ch,a.anim)
        if a.window:window(ch,A)
        else:print(gifs(ch,A,os.path.join(a.out,'preview')))
if __name__=='__main__':main()
