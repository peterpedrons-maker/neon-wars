# Hearthblade (lendas-de-taverna/mmo) — decisões do dono do jogo

**Leia este arquivo no começo de toda sessão e acrescente aqui toda decisão nova que o dono disser.** Pedidos viram regra permanente, não são só da conversa.
O dono fala português e joga pelo celular (app). Prefere respostas diretas; prompts de imagem devem ser enviados no chat, cada um em um bloco de código separado e completo (um toque para copiar).

## Visão do jogo
- ARPG automático por enquanto; **quando ficar pronto, vira manual** (o jogador precisa reconhecer drops únicos/bons só pelo drop: som, feixe de luz, cor).
- **Vai até o nível 60.** Quer **MUITAS dungeons**, não poucas. Dungeons devem ser **agrupadas por faixa de nível**: o jogador tem **escolhas diferentes no mesmo nível** (ex.: uma floresta nível 1; floresta 2 e esgoto liberam juntos, e o jogador escolhe). Cada dungeon dropa coisas diferentes (equipamentos/materiais específicos), como em MMOs. **Ainda não fazer isso**: está em fase de teste.
- **Teste: todas as dungeons e arenas ficam abertas** (flag `TEST_UNLOCK` em `index.html`) para não precisar subir de nível. Não desligar sem o dono pedir.
- Próximos cenários: **fechados e coerentes (salas/corredores, como a Cripta)**, não florestas abertas.
- Ideia aprovada de chefe: **sapo gigante do esgoto**, que fica submerso (sombra nadando → emerge, patas apoiadas, dispara projéteis). Só depois da Cripta. Kit sugerido: Língua, Chuva de bolhas, Maré, Mergulho. Esgoto fechado novo.
- **Cada chefe tem kit único** (nada de todos com investida/rugido/invocação). Rei Esquecido: Esquecimento, Eco, Fenda do Vazio, Coroa de Almas, Trevas.

## Visual e arte
- **2.5D (three.js) é o único visual.** Cenários gerados por código (`v3.js`, `v3proc.js`), sem depender de imagens do dono para cenário.
- **Personagens, inimigos e chefes SEMPRE são os sprites de arte já existentes** (LPC e as artes de IA enviadas). Nunca desenhar personagem por código.
- **Movimento = estilo miniatura de RPG tático/Paper Mario:** poses estáticas (parado, ataque, dano, morte); não existe pose de andar. Anda **um pedaço, salta, pousa, fica parado, repete.** Não deslizar, não quicar contínuo. Voadores flutuam.
- Efeitos (raio, aura, rastro, runa) devem ser **feitos por código**, não desenhados no sprite; pedir ao dono imagens **sem** efeitos, **uma imagem por pose** (sem variações/quadros).
- Câmera mais próxima em todos os mapas. Zoom out cinematográfico em chefe/mini-chefe e nas habilidades de longo alcance. Jogador e inimigos ficam visíveis atrás de objetos (contorno).
- Água com ondas e peixes; rochas grandes bloqueiam o herói; vida no cenário (pássaros, borboletas, folhas).

## Interface e economia
- **Vender só no Mercador** (estilo MMO). Mochila tem **100 espaços**. Nada de venda automática. Mochila cheia = item fica no chão com aviso. Poção automática fica na **mochila**.
- Números de combate claros: crítico, dano recebido, cura, poção, roubo de vida; com som. Drops: som por raridade + feixe de luz.
- Chefes: **barra de canalização com nome da habilidade** acima deles antes de cada habilidade.
- Sons: refinar sempre; som de arma por tipo (aço, machado, martelo, adaga); magia com som de poder mágico (não madeira).

## Combate
- Chefe não pode empurrar o herói até o canto; dá a volta se ele estiver encurralado.
- Mini-chefes têm arte própria (Xamã Skrix, Morcego-Vampiro, Capitão Presa-de-Ferro, Boticário Podre) e devem nascer perto do herói.

## Chefes e criaturas com arte própria (já no jogo)
Grunk (goblin), Morvath (esqueleto), Gorgash (ogro), Rei dos Ratos, **Rei Esquecido** (Cripta); Cripta: Cultista, Guarda-Caveira, Espectro, Gárgula, Zumbi Sineiro. O Pântano usa goblins/Grunk emprestados (falta arte própria).

## Fluxo de trabalho
- Trabalhar na branch `claude/test-game-new-repo-ja24p9`; para publicar: PR → merge (squash) na `main` (o Pages só publica a `main`). Conflitos de squash: `git merge origin/main` e `git checkout --ours`.
- O proxy do ambiente bloqueia o site publicado; não dá para conferir o deploy daqui, dizer isso ao dono.
- Testes: Chromium headless com `--use-angle=swiftshader`; servidor `python3 -m http.server 8760` na raiz do repo.

## Direção pixel art top-down (em teste, `lendas-de-taverna/mmo/proto_pixel/`)
- O dono quer **refazer o gráfico do jogo em pixel art top-down estilo 16 bits (SNES/NES)**, por código, com nível coerente (não precisa ser super elaborado). Referência: clareira com árvores, água e trilha de pedras enviada pelo dono.
- **Personagens andam de verdade**: ciclo de 4 poses (contato, passagem, contato oposto, passagem), braços em oposição às pernas, corpo sobe 1px na passagem. **Nada de saltinhos** (isso vale só para criaturas sem pernas, como o slime, que pula). Isso substitui a regra do "estilo miniatura" para o pixel art.
- **Arma é peça separada** da mão do personagem (contorno próprio, nunca fundida ao corpo); balança junto com o braço.
- Proporções de RPG 16 bits: cabeça ~1/3 da altura, cabeça de formato natural (nada de capacete/cúpula), 4 direções (frente, costas, lado; esquerda = espelho), rampas de 3–4 tons com troca de matiz (sombra mais fria, luz mais quente), **contorno seletivo** (escuro da própria cor, não preto puro).
- **Sistema atual (preferido): esqueleto 2D** `skel2d.py` (juntas + cinemática, sombreado volumétrico sem dither, contorno seletivo, arma separada, caudas com mola). Andar de **8 quadros**, parado de 8, **ataque de 10 poses com o corpo inteiro** (tronco, quadril, pernas, braço livre), goblin com reação (hurt/death). Cena de teste: `ataque.py`. O dono quer MAIS quadros por animação e ataques com corpo todo, nunca 3 poses secas. Vistas frente/costas ainda faltam neste sistema.
- Ferramentas antigas: `tools/mmo/pxengine/data/pxrig.py` (monta sprite por partes), `px2_hero.py`, `px2_mobs.py` (goblin/slime), `pxtool.py` (editor em grade/verificador), `andar2.py` (cena de teste). O Rei Esquecido ainda precisa ser refeito neste estilo (hoje é o mockup antigo `teste_rei.py`).
- Pesquisa feita: tutoriais de ciclo de andar em pixel art (4 frames, bob de 1px) e de contorno seletivo/hue shifting (Lospec, Slynyrd). O site slynyrd.com é bloqueado pelo proxy.
