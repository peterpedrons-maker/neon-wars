# Árvore de habilidades — rascunho

Combina com o que já está decidido: recarga **por turno** (sem mana) e IA que escolhe quando usar
(depois os gatilhos). O jogador escolhe **o que desbloquear**; atributos continuam automáticos.

## Regras
- **1 ponto de habilidade a cada 2 níveis** a partir do nível 2 (25 pontos no Nv 50, 30 no Nv 60).
- Cada classe tem 14 nós: **tronco** (4, todo mundo) + **2 ramos de 5**, um por subclasse.
  Com 25–30 pontos o jogador completa o tronco, um ramo e boa parte do outro: **há escolha**, não dá pra ter tudo.
- Nó exige o anterior do ramo. Botão **"Automático"** segue a ordem recomendada da subclasse.
- Ativa: gasta a ação do turno no lugar do ataque básico, com recarga em turnos. A IA usa a ativa quando está pronta
  e faz sentido (alvo isolado, aliado ferido, grupo de inimigos…).
- **Respec grátis** na Taverna.

## Guerreiro
| Nó | Tipo | Efeito | Recarga |
|---|---|---|---|
| **Tronco** Pele de Ferro | passiva | +10% PV máx. | — |
| Golpe Poderoso | ativa | dano ×1,5 em um alvo | 3 |
| Grito de Guerra | ativa | aliados a 3 casas: +2 acerto no próximo ataque | 5 |
| Firmeza | passiva | −2 de dano recebido por golpe | — |
| **Cavaleiro** Provocar | ativa | inimigos a 3 casas preferem atacá-lo por 2 turnos | 5 |
| Escudo Aliado | ativa | absorve 50% do próximo dano de um aliado adjacente | 4 |
| Muralha | passiva | +1 DEF por aliado adjacente (máx. +3) | — |
| Contra-golpe | passiva | 25% de revidar golpe corpo a corpo recebido | — |
| Bastião | ativa | 2 turnos sem sofrer crítico e −30% de dano | 6 |
| **Bárbaro** Golpe Giratório | ativa | atinge todos os inimigos adjacentes | 4 |
| Sede de Sangue | passiva | +1 dano por inimigo morto na batalha (máx. +5) | — |
| Selvageria | passiva | +10% de dano com menos de 50% de PV | — |
| Investida | ativa | avança até 4 casas e ataca com +2 de acerto | 4 |
| Fúria Final | ativa | ataca duas vezes no turno | 7 |

## Ladino
| Nó | Tipo | Efeito | Recarga |
|---|---|---|---|
| **Tronco** Pés Leves | passiva | +1 Movimento | — |
| Estocada Dupla | ativa | dois ataques com −2 de acerto | 3 |
| Mãos Leves | passiva | +3 em achar segredos | — |
| Evasão | passiva | 15% de desviar totalmente de um golpe | — |
| **Assassino** Golpe nas Costas | ativa | +4 acerto e dano ×1,5 em alvo isolado | 3 |
| Marcar Alvo | ativa | alvo sofre +20% de dano de todos por 2 turnos | 5 |
| Sombras | passiva | o primeiro golpe da batalha é crítico automático | — |
| Lâmina Envenenada | ativa | veneno por 3 turnos | 4 |
| Execução | passiva | dano ×2 contra alvos abaixo de 25% de PV | — |
| **Armadilheiro** Armadilha de Espinhos | ativa | coloca armadilha numa casa adjacente (dano + para o inimigo) | 5 |
| Fumaça | ativa | aliados a 2 casas: +3 DEF por 1 turno | 6 |
| Rede | ativa | prende um alvo por 1 turno (não anda) | 5 |
| Preparado | passiva | emboscada do 1º golpe passa de +3 para +6 | — |
| Campo Minado | ativa | 3 armadilhas em cruz | 8 |

## Mago
| Nó | Tipo | Efeito | Recarga |
|---|---|---|---|
| **Tronco** Mente Aguçada | passiva | +10% de dano mágico | — |
| Bola de Fogo | ativa | dano em área 3×3 | 3 |
| Escudo Arcano | ativa | absorve dano num aliado (ou nele) por 2 turnos | 4 |
| Passo Arcano | ativa | troca de lugar com um aliado a até 4 casas | 4 |
| **Piromante** Chama Viva | ativa | queimadura por 3 turnos | 3 |
| Explosão | passiva | área da Bola de Fogo +1 casa | — |
| Combustão | passiva | +crítico contra alvos queimando | — |
| Chuva de Meteoros | ativa | 3 explosões em casas aleatórias perto do alvo | 8 |
| Pirofagia | passiva | cura 10% do dano de fogo causado | — |
| **Geomante** Pele de Pedra | passiva | +3 DEF | — |
| Dardo de Rocha | ativa | dano forte que ignora 4 de DEF | 3 |
| Muralha de Terra | ativa | cria obstáculo temporário em 3 casas | 6 |
| Tremor | ativa | atordoa inimigos adjacentes por 1 turno | 5 |
| Terremoto | ativa | dano em área grande | 8 |

## Clérigo
| Nó | Tipo | Efeito | Recarga |
|---|---|---|---|
| **Tronco** Cura Maior | ativa | cura o dobro num aliado | 3 |
| Bênção | ativa | +2 acerto e +2 DEF num aliado por 2 turnos | 4 |
| Castigo | ativa | dano sagrado com Sabedoria (mira o inimigo mais forte) | 3 |
| Fé Inabalável | passiva | +2 Res. Mágica | — |
| **Curandeiro** Cura em Área | ativa | cura todos a 2 casas | 5 |
| Aura Vital | passiva | aliados adjacentes recuperam 2 PV por turno | — |
| Purificar | ativa | remove veneno e efeitos ruins de um aliado | 3 |
| Ressurgir | ativa | revive um aliado caído com 30% de PV (1× por batalha) | — |
| Milagre | ativa | cura total num aliado | 8 |
| **Templário** Golpe Sagrado | ativa | dano ×1,4 e recupera 30% do dano em PV | 3 |
| Escudo da Fé | passiva | +2 DEF | — |
| Punição | ativa | marca um alvo: aliados causam +2 de dano nele por 2 turnos | 4 |
| Luz Vingadora | passiva | +50% de dano contra mortos-vivos | — |
| Julgamento | ativa | dano sagrado em área | 7 |

## Arqueiro
| Nó | Tipo | Efeito | Recarga |
|---|---|---|---|
| **Tronco** Olhar de Águia | passiva | +1 Alcance | — |
| Tiro Certeiro | ativa | +4 acerto e dano ×1,3 | 3 |
| Flecha Perfurante | ativa | atinge dois alvos em linha | 4 |
| Agilidade | passiva | +1 Movimento | — |
| **Patrulheiro** Marca do Caçador | ativa | alvo marcado: +3 acerto e +2 de dano do arqueiro por 2 turnos | 4 |
| Foco | passiva | empilha +2 de acerto a cada golpe seguido no mesmo alvo | — |
| Posição Elevada | passiva | bônus de morro sobe de +4 para +6 | — |
| Tiro Mortal | ativa | dano ×2 | 7 |
| Armadilha de Caça | ativa | armadilha adjacente que prende o inimigo | 5 |
| **Saraivador** Chuva de Flechas | ativa | dano em área 3×3 | 4 |
| Ricochete | passiva | um segundo alvo adjacente leva 50% do dano | — |
| Rajada | ativa | três flechas com −2 de acerto | 4 |
| Munição Pesada | passiva | +3 de dano | — |
| Saraivada Total | ativa | dano em área grande | 8 |

## Bardo
| Nó | Tipo | Efeito | Recarga |
|---|---|---|---|
| **Tronco** Inspiração Maior | passiva | a balada dá +1 de acerto a mais | — |
| Canção de Vigor | ativa | cura leve em todos a 2 casas | 4 |
| Ritmo de Marcha | ativa | aliados a 3 casas: +1 Movimento por 2 turnos | 5 |
| Nota Aguda | ativa | dano sônico em dois alvos | 3 |
| **Consonante** Hino de Coragem | ativa | aliados a 3 casas: +2 dano por 2 turnos | 5 |
| Harmonia | passiva | a balada inspira dois aliados | — |
| Coro | passiva | +1 dano por aliado a 2 casas | — |
| Canção de Ninar | ativa | inimigos adjacentes perdem a próxima ação | 7 |
| Concerto Final | ativa | todos os aliados: +2 acerto, +2 DEF, +2 dano por 2 turnos | 8 |
| **Dissonante** Desafinar | ativa | −3 DEF no alvo por 2 turnos | 3 |
| Grito Estridente | ativa | dano em área e deixa "abalados" | 5 |
| Eco | passiva | efeitos ruins que o bardo aplica duram +1 turno | — |
| Cacofonia | ativa | inimigos na área erram mais: −3 de acerto por 2 turnos | 6 |
| Sinfonia do Caos | ativa | dano em área e debuffs juntos | 8 |

## Mecânicas novas que isso exige (por custo)
1. **Baratas:** passivas de número (PV, Mov, Alc, DEF, dano), dano ×N, ataque duplo, marca/debuff com duração
   (hoje só existem "abalado" e "inspirado" de 1 golpe).
2. **Médias:** dano em área (adjacentes, 3×3, em linha), avanço + ataque, provocar (alvo preferido), escudo de absorção,
   queimadura/veneno por turno (veneno já existe), cura em área, atordoar/prender.
3. **Caras:** armadilha colocável no chão, obstáculo temporário, reviver, trocar de lugar.
Ordem sugerida: implementar o tronco e um ramo de cada classe primeiro (médias), deixar as caras pro final.

## Cuidados
- Habilidades não devem anular o d20: ataque especial usa o mesmo teste de acerto, só muda dano/alcance/efeito.
- Recargas contam turnos do próprio herói; a lista de turno já mostra isso bem.
- Tela da árvore: mockup antes de implementar (como combinado), na ficha do herói.
