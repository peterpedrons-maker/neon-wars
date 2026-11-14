#!/usr/bin/env python3
"""Junta as medidas de varios golpes reais (saida do bvh_features.py) e gera os alvos do avaliador.
uso: python3 bvh_features.py *.bvh > f.json ; python3 calibrar.py f.json > ../calibracao.json
Os alvos usam a mediana dos golpes reais; a altura do Rei e 4,4 unidades."""
import sys,json,statistics as st
H=4.4;rows=[r for p in sys.argv[1:] for r in json.load(open(p)) if 'erro' not in r and r.get('pico_vel',0)>1 and r.get('t_pico',0)>.1]
if len(rows)<3:
    print(json.dumps({'erro':'poucos golpes validos (%d); precisa de pelo menos 3 arquivos com golpes'%len(rows)},ensure_ascii=False));sys.exit(1)
med=lambda k:st.median(r[k] for r in rows)
cal={'amostras':len(rows),'snap':round(med('explosao')*.8,2),'ant':round(med('antecipacao_altura')*H*.8,2),'fol':round(max(.15,med('continuacao_altura')*H*.8),2),
 'pico_vel':round(med('pico_vel')*H,1),'t_subida':round(med('t_subida'),2),'t_descida':round(med('t_descida'),2),'variacao_quadril':round(med('variacao_quadril')*H,2)}
print(json.dumps(cal,indent=1,ensure_ascii=False))
