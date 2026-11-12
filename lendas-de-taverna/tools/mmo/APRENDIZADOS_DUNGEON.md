# Aprendizados: montar dungeons com peças separadas (Cripta)

Regras que apareceram ao montar a Cripta do Rei Esquecido. Valem para qualquer dungeon nova. O script de referência é `cripta_montar.py`.

## 1. Perspectiva (câmera de cima, ~45°)
- **Parede vertical sempre por cima da horizontal.** Em qualquer encontro (canto de sala, entrada de corredor, T), a parede vertical aparece inteira, do topo até o pé, e a horizontal bate atrás dela. A face lateral de uma parede fechada não é visível.
- **Parede de baixo (sul) mostra a face de fora.** É um bloco alto, desenhado *depois* do personagem, e cobre uma faixa do chão. A de cima (norte) mostra a face de dentro, desenhada *antes*.
- **Nada decorativo na face de fora** (estandarte, tocha, teia). Isso só existe nas paredes de dentro.
- **Cantos:** as laterais sobem até o topo da parede norte e a faixa norte fica *entre* elas, nunca por cima.
- **Portas:** o arco tem a mesma pedra de capa que a parede, em linha contínua por cima. O vão mostra o *chão* iluminado, não preto. O herói passa *por baixo* do arco: a pedra do arco (sem o vão) é desenhada sobre ele enquanto estiver dentro do vão.

### Viga (capa de pedra) e contorno
- A **viga** é a capa de pedra clara no topo de cada parede. Todas as vigas de uma sala formam um **contorno fechado**: norte, sul e as duas laterais se encontram em quadrados de canto.
- **Laterais param na viga da parede sul**, sem descer ao lado da face. A face (tijolos) da parede sul passa por baixo, na largura toda, inclusive embaixo dos cantos. É igual ao encontro de cima.
- **Corredor:** as laterais dele nascem na viga da parede sul da sala de cima e descem até a viga da faixa da sala de baixo.
- **Arco:** é menor que a parede (escala ~0,86) e fica **encaixado abaixo** da viga, que corre reta por cima dele. Largura menor que a do corredor. Nunca colar a viga por cima do arco.
- Peças vizinhas (tochas, estandartes) não podem se sobrepor nem ser cortadas; tochas duplicadas a menos de 110 px são descartadas.

## 2. Camadas (ordem de desenho)
1. Chão, tapete, parede norte, objetos de fundo
2. Personagens e objetos, ordenados pelo pé (y)
3. Camada da frente: parede sul, laterais, moldura do arco, parte de cima de objetos altos
- **Bolha:** onde a camada da frente cobre o herói, a parede fica translúcida num círculo suave em volta do tronco, com um anel claro. Raio ~34–70 px, transparência ~86%. O herói nunca some inteiro: a colisão limita o quanto ele entra atrás da parede.

## 3. Colisão
- Vem da **geometria das peças**, não da cor da imagem. A máscara por cor falhou: atravessava paredes e travava em arcos.
- Andável = chão com 14 px de folga das paredes; vão da porta e corredor = passagem contínua; objetos = caixa na base (~55% da largura).
- **Sempre** verificar por flood-fill a partir da entrada que todas as salas são alcançáveis.

## 4. Objetos e decoração
- Poucos, simétricos, **nunca soltos no meio**: perto de paredes, cantos ou eixo da sala.
- **Nunca em cima do tapete** nem do caminho da porta.
- Estandarte só inteiro (sem corte) e longe do arco; tochas fogem dos estandartes (> 70 px).
- Peças de parede com suporte de tocha sem chama não entram: as tochas animadas são colocadas à parte.

## 5. Arte gerada por IA: o que funciona
- **Mapa inteiro por IA** não serve: perde a camada de parede, fica borrado ao ampliar e a colisão sai errada. Ampliar com OpenCV melhora pouco.
- **Peças separadas por folha** (chão, paredes, laterais, portas) funcionam: recorta-se por componentes conexos sobre fundo magenta, com margem grande entre as peças.
- Tiles de chão: cortar a moldura (14 px) antes de repetir; testar a emenda. Pisos com lajes de tamanho diferente (peça "grande"/"rachado") ficam fora do sorteio.
- Escala usada: peças × 0,5; laje ≈ 42 px; parede ≈ 147 px de altura; herói a 2× (96 px).
- Prompts: começar sempre pela mesma frase de estilo e pedir "fundo magenta, espaço grande entre peças, sem sombra".

## 6. Processo
- Olhar o mapa em **recortes 1:1** de cada encontro (cantos, portas, entradas de corredor), não só a visão geral.
- Corrigir uma regra por vez e anotá-la aqui.
