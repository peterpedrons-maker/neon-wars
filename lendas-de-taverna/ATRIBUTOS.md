# Sistema de atributos (proposta — estilo D&D 5e)

Decisões do dono: 6 atributos do D&D; level up com perfil fixo da classe + pontos livres;
itens com afixos sorteados; inimigos com nível e atributos iguais aos heróis.
Todos os números abaixo são **ponto de partida**, a calibrar com o modelo de simulação
(`BALANCEAMENTO.md`) antes de valer.

## 1. Atributos
Força (FOR) · Destreza (DES) · Constituição (CON) · Inteligência (INT) · Sabedoria (SAB) · Carisma (CAR).
Valor 1–30. **Modificador = ⌊(valor − 10) / 2⌋** (valor 10 → +0, 14 → +2, 20 → +5).
Substitui os 5 atributos de hoje (Força/Destreza/Inteligência/Vitalidade/Fé; Vitalidade→CON, Fé→SAB).

## 2. O que cada atributo faz (tudo continua sendo d20 + ATQ ≥ DEF)
| Atributo | Efeito |
|---|---|
| FOR | acerto e dano de armas corpo a corpo |
| DES | acerto e dano de arco/adagas; **DEF** (até o limite da armadura); iniciativa; crítico a partir de +4 |
| CON | PV por nível; resistência a veneno/armadilhas |
| INT | acerto e dano de magia ofensiva (Mago); segredos escondidos |
| SAB | cura e magia de fé (Clérigo); **Res. Mágica**; percepção (achar segredos) |
| CAR | força da inspiração do Bardo; chance de drop e preço de venda |

Atributo de ataque da classe: Guerreiro FOR · Ladino DES · Arqueiro DES · Mago INT · Clérigo SAB · Bardo CAR.

## 3. Valores derivados (mesma fórmula para herói e inimigo)
- **Bônus de proficiência** = 2 + ⌊(nível − 1) / 4⌋ (Nv1 +2 … Nv25 +8 … Nv50 +14).
- **ATQ** = bônus de proficiência + mod do atributo de ataque + itens.
- **DEF** = 10 + armadura base da classe + mod DES (limitado: pesada 0, média +2, leve sem limite) + itens.
- **Res. Mágica** = 10 + mod SAB + metade da armadura base + itens.
- **PV** = PV base da classe (valor de hoje) + por nível (dado de vida fixo da classe + mod CON, mín. 1) + itens.
  Dado de vida fixo: Guerreiro 6 · Clérigo 5 · Ladino/Arqueiro/Bardo 4 · Mago 3.
- **Dano** = dado da arma + mod do atributo de ataque + itens (substitui ⌊(FOR+INT)/3⌋).
- **Iniciativa** = base da classe + mod DES. **Cura** = dado + mod SAB. **Segredos** = mod SAB + mod INT/2 + itens.
- Movimento e alcance continuam vindo da classe e dos itens (não de atributo).
Resultado: o nível agora sobe ATQ (proficiência), PV, dano e DEF (via DES), e todas as
classes crescem em dano (hoje Ladino, Arqueiro e Clérigo não crescem).

## 4. Subir de nível
- **Perfil fixo por classe:** 1 ponto por nível distribuído conforme pesos da classe
  (acumula frações). Ex.: Guerreiro FOR 0,5 · CON 0,3 · DES 0,2; Mago INT 0,6 · CON 0,2 · DES 0,2.
- **Pontos livres:** +1 ponto a cada 2 níveis para o jogador distribuir (tela na ficha do
  herói). Se o jogador não gastar, vale o perfil da classe (o jogo continua jogando sozinho).
- Teto de 30 por atributo; pontos extras além disso não se perdem (ficam guardados).

## 5. Itens com afixos sorteados
- Cada item = **base** (tipo + espaço, ícone do pack) + **afixos** sorteados + **nível do item**.
- Nº de afixos pela raridade: Comum 1 · Raro 2 · Mágico 3 · Épico 4 · Lendário 5 (+1 propriedade única).
- Pool de afixos por espaço: atributos (+FOR…+CAR), ATQ, DEF, Res. Mágica, PV, dano, crítico,
  Mov/Alc (só alguns espaços), segredos. Armas puxam mais ATQ/dano; armaduras DEF/PV; acessórios atributos.
- **Nível do item = nível do mapa.** Valor do afixo cresce com o nível do item
  (ex.: +1 atributo no Nv1 → +5 no Nv50); raridade aumenta quantidade, não o teto de cada afixo.
- Chance de raridade depende do ato (atos iniciais quase só comum/raro; épico/lendário só do meio pra frente);
  chefe garante raridade mínima 3. Nome gerado: base + prefixo/sufixo ("Espada Afiada do Urso").
- Itens antigos do save viram bases com afixos fixos equivalentes (sem perder nada).

## 6. Inimigos
- Cada espécie ganha um **bloco de 6 atributos**, um perfil de crescimento (como a classe) e armadura base;
  o **nível vem do mapa** (+2 pro chefe, +1 pro líder). Mesmas fórmulas da seção 3 calculam
  ATQ, DEF, Res. Mágica, PV e dano. **A `escala` atual deixa de existir.**
- Cada espécie tem dado de dano e dado de vida fixos (Goblin 1d6, Ogro 1d12, Troll 1d12…).
- XP por inimigo = valor base × fator do nível (hoje é fixo, e não acompanha o mapa).

## 7. Ordem de trabalho
1. Motor: atributos, derivados, level up, inimigos (sem mudar telas; teste automatizado dos números).
2. Itens com afixos + migração dos saves.
3. Telas (mockup antes): ficha com 6 atributos e pontos livres, itens com afixos, Forja/Cofre.
4. Calibração com o modelo de simulação: curva de XP, nível por mapa, raridade por ato, limite de rodadas.
5. Testes de batalha completos nos mapas novos.
