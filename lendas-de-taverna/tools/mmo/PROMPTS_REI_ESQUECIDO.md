# Rei Esquecido — kit de habilidades e prompts das poses

## Por que um kit novo
Grunk, Gorgash, Morvath e o Rei dos Ratos usam variações de investida, rugido e invocação. O Rei Esquecido foi desenhado para mexer com
**o que o jogador faz**, não só com onde ele pisa. Tema: o rei que ninguém lembra — memória, vazio e escuridão. **Já está implementado no jogo**
(com a animação do Morvath como provisória até chegarem as poses novas).

| Habilidade | O que faz | Como o jogador reage |
|---|---|---|
| **Esquecimento** | Aponta para você e apaga uma habilidade equipada por 9 s (entra em recarga) | Planejar com as outras habilidades; poção/esquiva ganham valor |
| **Eco** | Marca o chão onde você está; **depois de um instante repete o golpe onde você foi parar** | Não adianta só sair do círculo: precisa prever o segundo |
| **Fenda do Vazio** | Corta o ar em leque de 3 cortes seguidos | Ler o ângulo e escolher o vão |
| **Coroa de Almas** (abaixo de 65% de vida) | 4 almas giram em volta dele e ele leva só 20% do dano até todas serem destruídas | Troca de alvo: quebrar as almas primeiro |
| **Trevas** (abaixo de 40%, uma vez) | Apaga as luzes: só se enxerga ao redor do herói e do chefe por ~14 s; ele fica mais agressivo | Posicionamento sem ver o chão inteiro |

Golpe básico: varredura lenta e pesada de arma, sem rugido nem investida.

## Prompts das poses (uma folha por pose)
Já temos: **parado** e **levantando (preparando o ataque)**. Envie sempre as duas imagens como referência.

**Bloco fixo (cole no começo de TODO prompt):**
> Use as imagens de referência: o MESMO personagem (Rei Esquecido), mesmas proporções, armadura, coroa, cores, arma e estilo de pintura em pixel art
> 2.5D vista 3/4 de cima. Sprite sheet horizontal com N quadros iguais lado a lado, em sequência de animação, personagem sempre no mesmo
> tamanho e com os pés na mesma altura em todos os quadros, voltado para a DIREITA, fundo cinza-claro liso (#d9d9d9) sem chão, sem sombra, sem texto,
> sem moldura, nada cortado nas bordas.

1. **Andando — 8 quadros.** Ciclo lento e majestoso, passos largos, capa balançando, arma arrastando de leve; último quadro volta ao primeiro.
2. **Golpe básico — 7 quadros.** Arma para trás, varredura horizontal larga e pesada, rastro roxo, recuperação. O golpe cai no quadro 4.
3. **Esquecimento — 7 quadros.** Estende o braço livre para frente com o dedo/mão aberta apontando para o alvo; olhos e coroa brilham em roxo;
   uma luz escura sai da mão no quadro 4 e ele fecha a mão devagar, como quem apaga uma memória.
4. **Eco — 8 quadros.** Bate a arma no chão com uma mão (quadros 1–4), uma imagem translúcida e roxa dele mesmo se separa do corpo e repete o
   gesto um instante depois (quadros 5–8), como uma sombra atrasada.
5. **Fenda do Vazio — 7 quadros.** Arma elevada na diagonal, corta o ar de cima para baixo três vezes seguidas (quadros 3, 5 e 7), cada corte
   deixa uma linha de energia roxa que se abre como uma rachadura.
6. **Coroa de Almas — 8 quadros.** Braços abertos para cima, a coroa se ergue e brilha, quatro luzes/espíritos pequenos saem da coroa e começam
   a girar ao redor dele (os espíritos só aparecem aqui, em quadros finais, bem pequenos).
7. **Trevas — 8 quadros.** Fecha os punhos junto ao peito, corpo envolto em névoa roxa que escurece em volta, olhos acesos; abre os braços no
   quadro 6 e a escuridão se espalha. Funciona também como entrada da fase final.
8. **Levando dano — 4 quadros.** Corpo recua e se contorce, arma abaixa, clarão branco-roxo no primeiro quadro, recompõe-se no último.
9. **Morte — 8 quadros.** Cambaleia, ajoelha, a coroa cai e racha, a armadura vira pó e fumaça roxa, termina quase vazio (último quadro estável).

**Efeitos separados (cada um em uma imagem própria, fundo liso):**
10. **Alma presa — 4 quadros em loop:** pequeno espírito de caveira com chama roxa, olhos acesos, pairando (é o que gira na Coroa).
11. **Selo de Esquecimento — 1 imagem quadrada:** glifo/runa roxa circular vista de cima (aparece no chão e sobre o jogador).

**Dicas:** peça 4 variações de cada e escolha a mais fiel; se o rosto/armadura mudar, repita com "mantenha EXATAMENTE a mesma armadura e
coroa da referência". Quando as folhas ficarem prontas, envie e eu monto o atlas como o do Morvath e troco o provisório.

---

## Próximos chefes: não repetir kit
**Sapo do esgoto (ideia do dono do jogo):** fase 1 só sombra nadando; fase 2 emerge com as patas apoiadas, meio submerso, e dispara leques de
projéteis; fase 3 mergulha e reaparece em outro ponto com ondas de choque. Kit sugerido: **Língua** (puxa o herói para a água),
**Chuva de bolhas** (projéteis em leque), **Maré** (a água sobe e cobre parte da arena), **Mergulho** (some e reaparece onde você está).
Não usa investida, rugido nem invocação.
