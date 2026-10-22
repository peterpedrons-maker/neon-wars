# SpritePilot — índice dos pacotes

7 pacotes de pixel art da SpritePilot (https://spritepilot.com), licença
**CC0 1.0** em todos (domínio público — uso livre, sem precisar creditar).
Cada pasta tem seu próprio `LICENSE.txt`/`README.txt` originais, mantidos
pra referência.

Formato: cada efeito é uma *strip* — um PNG só, com todos os quadros lado
a lado numa fileira, em 16px e 32px. O `<pacote>-pack.json` de cada pasta
lista o número de quadros e o fps pensado pra cada um (`frames`, `fps`,
`loop`), prontos pra tocar com a mesma técnica de recorte por UV já usada
nos sprites LPC (`lpcSetUV` em `index.html`), só que numa única fileira
em vez de grade 4 direções.

## O que tem em cada pacote

**combat/** — golpes e impactos: espada, garra, estilhaço de arma de
fogo, raio laser, flecha, aparar, onda de choque, crítico, pisão.

**magic/** — efeitos de magia: bola de fogo, estilhaço de gelo, orbe de
energia, raio, nuvem de veneno, aura de cura, bolha de escudo, portal,
teleporte.

**weather/** — clima ambiente: chuva, respingo de chuva, raio, neve,
folhas caindo, nuvem passando, rajada de vento, vaga-lumes, bolhas.

**environment/** — cenário animado: água, lava, cachoeira, tocha de
parede, estandarte, porta, armadilha de espinhos, bloco desmoronando,
grama alta.

**pickups/** — itens coletáveis: moeda, gema, coração, chave, estrela,
poção, baú do tesouro, escudo, raio, orbe de vida extra.

**ui/** — feedback de interface: balão de alerta (!), balão de pergunta
(?), check, X, batimento cardíaco, spinner de carregamento, seta
indicadora, level up, marcador de alvo.

**creatures/** — bichinhos animados (giro único, não direcional como os
heróis LPC): morcego, slime, fantasma, abelha, peixe, pássaro, aranha,
besouro. Bons pra decoração/ambiente ou inimigos pequenos — não têm
quadros de ataque/dano/direção como o pacote LPC, só um loop de
movimento.

## Ideias já discutidas com o usuário pra usar isso

- Balão de alerta/pergunta (`ui/alert-bubble`, `ui/question-bubble`) no
  lugar do ícone estático de "!"/"?" do Quadro de Missões.
- `environment/water` e `environment/waterfall` pra enriquecer o rio do
  tabuleiro (hoje é só uma textura com scroll).
- `weather/rain`, `weather/snow`, `weather/fireflies` pra variar o clima
  da vila/batalha por fase ou bioma.
- `magic/fireball`, `magic/ice-shard` etc. como efeito visual de ataque
  mágico do Mago, no lugar/complemento do burst de partículas atual.
- `creatures/bat`, `creatures/bee` etc. como bichos de ambiente
  decorativos na vila (igual os moradores que já andam por lá).
