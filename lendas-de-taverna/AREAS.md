# Áreas, mira no chão e IA tática — proposta (aguardando aprovação)

Diagrama: `mockups/areas-formas.png`.

## 1. Formas de área (cada habilidade escolhe a sua)
| Forma | Como funciona | Exemplos |
|---|---|---|
| Explosão (raio N) | casas a até N da casa mirada | Bola de Fogo (1), Chuva de Meteoros (2) |
| Quadrado 2×2 | 4 casas a partir da casa mirada | Cura em Área, Grito Estridente |
| Cruz | a casa mirada + as 4 direções | Raio Sagrado |
| Nova | em volta de quem lança (não acerta quem lança) | Giratório, Terremoto |
| Linha | da casa ao lado de quem lança, na direção da mira, até L casas | Muralha de Chamas, Flecha Perfurante |
| Cone | abre em leque na direção da mira | Sopro Gélido, Saraivada Total |
| Parede | linha de 3–5 casas cruzando a mira | Muralha de Terra, Rede |
| Raio encadeado | pula entre alvos a até 2 casas | Raio |

## 2. Regras
- **Acerta todo mundo na área**: aliados e inimigos, em dano, cura, buff e debuff (cura em área cura o inimigo que estiver dentro).
- Quem lança só entra na área se a casa dele estiver nela (nunca nas formas "ao redor").
- **Mira no chão**: a habilidade mira uma *casa* dentro do alcance, não só um personagem. Direção das linhas/cones = de quem lança até a casa mirada.

## 3. IA e o atributo Tática
- **Tática** (nova estatística derivada, aparece na ficha) = combinação de Inteligência (peso 2), Sabedoria e Destreza.
- A IA avalia as casas de mira possíveis e pontua: dano/cura/status em inimigos e aliados (± por abate, por inimigo ferido, por aliado atingido, por status útil).
- Quanto maior a Tática: examina mais casas (inclusive chão vazio), erra menos a escolha, evita fogo amigo, e escolhe melhor onde ficar para lançar. Tática baixa: mira só em personagens, às vezes acerta aliado ou escolhe o 2º melhor.
- Efeito no jogo: o jogador monta o grupo escolhendo heróis com atributos que combinam com o papel (Mago/Clérigo com Tática alta; Guerreiro nem tanto).

## 4. Fases de implementação
1. Motor: formas + mira no chão + fogo amigo em tudo + pontuação da IA (substitui `kind:'aoe'` e os buffs em raio).
2. Converter as habilidades atuais para formas e criar as novas (Muralha de Chamas, Sopro Gélido, Cura em Área, Raio…).
3. Mostrar a área na batalha (casas coloridas durante a mira) e um mini desenho da forma na descrição da habilidade.
4. Tática na ficha e no level up; ajuste de balanceamento (dano em área sem 75%, muralhas viram zonas depois).
