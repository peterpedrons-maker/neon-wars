# Árvores de habilidades — versão 2 (grafo ARPG, com status e movimento)

Formato (decidido): uma árvore por classe, em grafo. **Pequeno** (custo 1: +atributo/valor), **médio** (custo 2: passiva,
melhora ativa vizinha) e **grande** (custo 3: ativa ou passiva-chave). 1 ponto por nível a partir do nível 2; ~70 nós por
classe, ninguém pega todos. Respec grátis; botão "Automático". Ativas gastam a ação do turno, têm recarga em turnos e usam o
mesmo teste de acerto do ataque normal. Status em `STATUS.md`.

## O que muda o jeito de jogar (eixos)
- **Movimento:** Dar a Volta/Passo Lateral (andar depois de atacar), Investida, Recuar, Passo Sombrio, Passo Arcano, Escalador (sobe 1 altura a mais).
- **Altura:** hoje morro dá +2 de acerto. As árvores ampliam: dano por altura, alcance e acerto no alto, "queda" (atacar de cima pra baixo).
- **Status:** cada classe aplica status e tem passivas que **pagam mais** contra alvos com um grupo de status ([DoT], [Controle], [Fraqueza]).
- **Terreno:** armadilhas, muralhas, zonas de fogo/gelo.

## Guerreiro — frente de batalha
**Tronco:** Pele de Ferro (P) +10% PV · Golpe Poderoso (A) dano ×1,5, recarga 3 · Dar a Volta (P) pode andar 2 casas depois de atacar · Firmeza (P) −2 de dano recebido.
**Cavaleiro (defesa/controle):**
Provocar (A) Provocado em inimigos a 3 casas por 2 turnos, 5 · Escudo Aliado (A) dá Escudo a um aliado adjacente, 4 ·
Muralha (P) +1 DEF por aliado adjacente (máx. +3) · Terreno Sagrado (P) em morro: +2 DEF e −20% de dano recebido ·
Punho Vingativo (P) +1 dano a cada golpe recebido na batalha (máx. +6) · Bastião (A) Inabalável por 2 turnos, 6.
**Bárbaro (ofensa/altura):**
Golpe Giratório (A) todos os adjacentes + Abalado, 4 · Corte Profundo (A) aplica Sangramento, 3 ·
Investida (A) avança 4 casas e ataca; descendo de morro, +15% de dano por nível de altura, 4 · Sede de Sangue (P) +1 dano por morte (máx. +5) ·
Selvageria (P) +10% de dano com menos de 50% de PV · Queda Pesada (P) atacando de cima: +25% de dano por nível de altura (máx. +50%) ·
Carniceiro (P) +30% de dano contra alvos Sangrando ou Abalado · Fúria Final (A) ataca duas vezes; depois fica Abalado 1 turno, 7.
**Pontes:** Veterano (P) +PV e dano · Passo Lateral (P) pode andar 1 casa antes de atacar.

## Ladino — mobilidade e oportunidade
**Tronco:** Pés Leves (P) +1 Mov · Estocada Dupla (A) dois ataques com −2 acerto, 3 · Evasão (P) 15% de desviar · Mãos Leves (P) +3 em segredos.
**Assassino (marcar e executar):**
Golpe nas Costas (A) +4 acerto e ×1,5 em alvo isolado ou flanqueado, 3 · Marcar Alvo (A) Marcado, 5 ·
Predador (P) +30% de dano contra [Controle] ou Marcado · Sombras (P) Furtivo no começo de cada batalha ·
Lâmina Envenenada (A) Veneno, 4 · Execução (P) ×2 abaixo de 25% de PV · Passo Sombrio (A) teleporta até 5 casas para o lado ou atrás de um inimigo, 5.
**Armadilheiro (terreno e controle):**
Armadilha de Espinhos (A) dano + Preso, 5 · Rede (A) Preso 2 turnos, 5 · Fumaça (A) aliados a 2 casas Protegidos e inimigos Cegos 1 turno, 6 ·
Preparado (P) emboscada +6 · Mestre do Terreno (P) +1 Mov e sobe 1 altura a mais · Gatuno (P) +30% de dano contra Preso ou Lento · Campo Minado (A) 3 armadilhas em cruz, 8.
**Ponte:** Esquiva Ágil (P) ao ser atacado de perto, 20% de andar 1 casa livre.

## Mago — área e elementos
**Tronco:** Mente Aguçada (P) +10% de dano mágico · Bola de Fogo (A) área 3×3, 3 · Escudo Arcano (A) Escudo em aliado ou nele, 4 · Passo Arcano (A) troca de lugar com um aliado a 4 casas, 4.
**Piromante (fogo/DoT):**
Chama Viva (A) Queimadura, 3 · Explosão (P) área +1 casa · Combustão (P) +40% de dano e +crítico contra Queimando ·
Muralha de Chamas (A) zona de fogo de 3 casas por 3 turnos, Queimadura em quem entra, 7 · Pirofagia (P) cura 10% do dano de fogo ·
Chuva de Meteoros (A) 3 explosões perto do alvo, 8 · Brasa Longa (P) Queimadura dura +1 turno e empilha 1 vez.
**Geomante (gelo/controle):**
Pele de Pedra (P) +3 DEF · Dardo de Rocha (A) ignora 4 de DEF, 3 · Nevasca (A) área, Gelado, 6 · Tremor (A) Atordoa adjacentes 1 turno, 5 ·
Gelo Rachante (P) +40% de dano contra Lento, Gelado ou Preso · Alto Torreão (P) em morro: +2 Alcance e +2 acerto ·
Muralha de Terra (A) obstáculo temporário em 3 casas, 6 · Terremoto (A) área grande + Lento, 8.
**Ponte:** Choque Térmico (P) fogo em Gelado / gelo em Queimando: +50% de dano · Sábio (P) +Inteligência e Sabedoria.

## Clérigo — suporte sagrado
**Tronco:** Cura Maior (A) cura o dobro, 3 · Bênção (A) Protegido + Inspirado num aliado, 4 · Castigo (A) dano sagrado com Sabedoria, 3 · Fé Inabalável (P) +2 Res. Mágica.
**Curandeiro:**
Cura em Área (A) a 2 casas, 5 · Aura Vital (P) aliados adjacentes com Regeneração · Purificar (A) remove debuffs, 3 · Ressurgir (A) revive com 30% de PV, 1× por batalha ·
Luz Restauradora (P) o excedente da cura vira Escudo (25%) · Bênção Prolongada (P) buffs do clérigo duram +1 turno · Milagre (A) cura total + Regeneração, 8.
**Templário:**
Golpe Sagrado (A) ×1,4 e recupera 30% do dano, 3 · Punição (A) Marcado, 4 · Escudo da Fé (P) +2 DEF · Luz Vingadora (P) +50% de dano contra mortos-vivos ·
Advertência (A) Medo em adjacentes por 2 turnos, 6 · Zelo (P) +30% de dano contra [Fraqueza] · Julgamento (A) área sagrada; +50% de dano contra Marcado, 7.
**Ponte:** Passo Abençoado (P) +1 Mov e cura 3 PV ao chegar perto de aliado ferido · Devoto (P) +Sabedoria.

## Arqueiro — posição, altura e precisão
**Tronco:** Olhar de Águia (P) +1 Alc · Tiro Certeiro (A) +4 acerto e ×1,3, 3 · Flecha Perfurante (A) dois alvos em linha, 4 · Agilidade (P) +1 Mov · Recuar (A) anda 3 casas para longe sem sofrer ataque, 4.
**Patrulheiro (foco e altura):**
Marca do Caçador (A) Marcado + Foco, 4 · Foco (P) +2 acerto por golpe seguido no mesmo alvo · Posição Elevada (P) em morro: +6 acerto e +25% de dano ·
Tiro Mortal (A) ×2, 7 · Armadilha de Caça (A) Preso, 5 · Instinto (P) +30% de dano contra Marcado ou Preso · Escalador (P) sobe 1 altura a mais.
**Saraivador (área e DoT):**
Chuva de Flechas (A) área 3×3, 4 · Rajada (A) três flechas com −2 acerto, 4 · Flecha Incendiária (A) Queimadura, 4 · Ricochete (P) segundo alvo leva 50% ·
Flechas Venenosas (P) 20% de chance de Veneno em todo golpe · Munição Pesada (P) +3 de dano · Saraivada Total (A) área grande, 8.
**Ponte:** Olho Treinado (P) +1 de crítico · Disparo em Movimento (P) pode atirar depois de andar sem penalidade.

## Bardo — apoio e debuff
**Tronco:** Inspiração Maior (P) balada +1 acerto · Canção de Vigor (A) Regeneração em área, remove Medo, 4 · Ritmo de Marcha (A) Veloz nos aliados, 5 · Nota Aguda (A) dano sônico em dois alvos, 3.
**Consonante (buffs):**
Hino de Coragem (A) Fortalecido nos aliados a 3 casas, 5 · Harmonia (P) a balada inspira dois aliados · Coro (P) +1 dano por aliado a 2 casas ·
Marcha Triunfal (A) aliados ganham +2 Mov e +2 dano no primeiro golpe, 6 · Eco Benigno (P) buffs do bardo duram +1 turno ·
Canção de Ninar (A) Atordoa adjacentes 1 turno, 7 · Concerto Final (A) todos os aliados Fortalecidos + Protegidos + Inspirados, 8.
**Dissonante (debuffs):**
Desafinar (A) Abalado (−3 DEF), 3 · Grito Estridente (A) área + Abalado, 5 · Cacofonia (A) Cego em área, 6 · Pavor (A) Medo, 6 ·
Eco (P) debuffs do bardo duram +1 turno · Maestro do Caos (P) +25% de dano contra alvos com 2 ou mais debuffs · Sinfonia do Caos (A) dano em área + debuffs, 8.
**Ponte:** Voz Alta (P) buffs e debuffs alcançam +1 casa · Carisma (P) +Carisma.

## Mecânicas novas (por custo)
1. **Sistema de status** (duração, empilhar, ícones, regras de imunidade) — base de tudo; vem primeiro.
2. Barato: passivas de número, dano ×N, ataque duplo, andar depois de atacar, bônus por altura/estado do alvo.
3. Médio: dano em área, avanço + ataque, provocar, escudo, cura em área, Medo, atordoar/prender.
4. Caro: armadilha no chão, obstáculo/zonas de fogo, reviver, teleportar/trocar de lugar, subir altura extra.

## Ordem de implementação sugerida
Status → motor de habilidades (ativa, recarga, IA usa) → tronco e um ramo por classe → pontes e ramos restantes → tela da árvore.
