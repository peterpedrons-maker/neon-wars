# Relatório de equipamentos — estado atual

Gerado a partir do catálogo real em `index.html` (constante `ITEMS`), não escrito
à mão — se o jogo mudar, este arquivo pode ficar desatualizado até a próxima
geração. Serve pra responder "o que já existe hoje", antes de decidir o que
muda com classes/subclasses.

## Resumo

- **80 itens** no total, em **8 posições de equipamento** por herói: arma, mão
  secundária, cabeça, corpo, mãos, pés e 2 acessórios (o slot `accessory`
  preenche o primeiro dos dois que estiver livre).
- **5 raridades**: Comum, Raro, Mágico, Épico, Lendário — cor própria na UI,
  mas por enquanto só cosmética (nenhuma raridade dá efeito especial ainda,
  só "mais número" nos mods).
- Classes de arma de duas mãos (**Mago, Arqueiro, Bardo** — e também o futuro
  Monge, se mantivermos ele como marcial sem arma de uma mão) não podem usar
  o slot de mão secundária.
- **Nenhum item tem efeito de gatilho hoje** — tudo é soma direta de atributo
  (`atk`, `def`, `mov`, `alc`, `per`, `dmgBonus`, `crit`, `maxhp`). Isso é
  exatamente o que a conversa de gatilhos/subclasses vai precisar mudar pros
  itens de raridade mais alta.
- **Itens podem repetir.** Hoje não existe nenhum controle de "já caiu esse
  item" — o sorteio de loot (`rollItem`) pode entregar a mesma Lâmina do
  Dragão duas vezes na mesma campanha. Isso ficou pendente de uma conversa
  anterior (sobre itens únicos de verdade) que foi pausada quando decidimos
  mudar de roguelite pra campanha contínua — vale retomar.
- **Nenhum item tem lore/texto de sabor** — só a descrição mecânica (`desc`).
- Equipamento hoje é **genérico por slot**, não por classe/subclasse: um
  Piromante e um Geomante, por exemplo, poderiam equipar exatamente os mesmos
  itens. Se a gente quiser afinidade de equipamento por subclasse (ex.: o
  Geomante prefere itens de DEF, o Piromante prefere itens de ATQ/crítico),
  isso ainda não existe e precisa ser desenhado.

## Catálogo completo

## Arma (14 itens)

| Raridade | Nome | Ícone | Efeito |
|---|---|---|---|
| Comum | Lâmina Simples | ⚔️ | +1 ATQ |
| Comum | Adaga Enferrujada | 🗡️ | +1 Movimento |
| Comum | Cajado Rústico | 🪵 | +1 Alcance |
| Raro | Lâmina Afiada | ⚔️ | +2 ATQ |
| Raro | Machado de Ferro | 🪓 | +2 dano, −1 DEF |
| Raro | Arco Reforçado | 🏹 | +1 ATQ, +1 Alcance |
| Mágico | Cajado Arcano | 🔮 | +2 ATQ, +1 Alcance |
| Mágico | Adaga Encantada | 🗡️ | +2 ATQ, +1 Movimento |
| Mágico | Martelo Rúnico | 🔨 | +4 dano, −1 Movimento |
| Épico | Lâmina do Dragão | 🗡️ | +3 ATQ, +6 dano |
| Épico | Cetro Celestial | 🔮 | +3 ATQ, +2 Alcance |
| Épico | Garra Sombria | 🦅 | +3 ATQ, +2 Movimento, −1 DEF |
| Lendário | Excalibur Partida | ⚔️ | +4 ATQ, +8 dano, +1 Alcance |
| Lendário | Cajado do Infinito | ✨ | +4 ATQ, +3 Alcance, Crítico com 19+ |

## Mão secundária (10 itens)

| Raridade | Nome | Ícone | Efeito |
|---|---|---|---|
| Comum | Broquel de Madeira | 🛡️ | +1 DEF |
| Comum | Adaga de Reserva | 🗡️ | +1 ATQ |
| Raro | Escudo Pequeno | 🛡️ | +2 DEF |
| Raro | Livro de Rezas | 📖 | +3 PV máx |
| Mágico | Escudo Espelhado | 🪞 | +2 DEF, Crítico com 19+ |
| Mágico | Adaga das Sombras | 🗡️ | +2 ATQ, +1 Movimento |
| Épico | Égide Dracônica | 🐉 | +4 DEF, +4 PV máx |
| Épico | Tomo Arcano | 📘 | +3 ATQ, +1 Alcance |
| Lendário | Escudo da Aurora | 🌅 | +5 DEF, +8 PV máx |
| Lendário | Adaga do Eclipse | 🌒 | +4 ATQ, +2 Movimento, Crítico com 18+ |

## Cabeça (10 itens)

| Raridade | Nome | Ícone | Efeito |
|---|---|---|---|
| Comum | Elmo de Recruta | 🪖 | +1 DEF |
| Comum | Capuz do Viajante | 🧢 | +1 Movimento |
| Raro | Elmo de Ferro | 🪖 | +2 DEF, −1 Movimento |
| Raro | Capuz do Batedor | 🥷 | +2 pra achar segredos, +1 Movimento |
| Mágico | Coroa Arcana | 🔮 | +2 ATQ, +1 Alcance |
| Mágico | Elmo com Chifres | 🤘 | +4 dano, −1 DEF |
| Épico | Elmo do Campeão | ⚜️ | +3 DEF, +4 PV máx |
| Épico | Capuz dos Sussurros | 🌀 | +3 pra achar segredos, Crítico com 19+ |
| Lendário | Máscara do Vazio | 🎭 | +5 ATQ, Crítico com 18+ |
| Lendário | Coroa Eterna | 👑 | +12 PV máx, +3 DEF, +1 Movimento |

## Corpo (10 itens)

| Raridade | Nome | Ícone | Efeito |
|---|---|---|---|
| Comum | Gibão Simples | 🧥 | +2 PV máx |
| Comum | Colete de Couro | 🦺 | +1 DEF |
| Raro | Cota de Malha Leve | ⛓️ | +4 PV máx, +1 DEF |
| Raro | Manto do Viajante | 🧳 | +1 Movimento, +2 PV máx |
| Mágico | Capa Élfica | 🧵 | +2 DEF, +1 Movimento |
| Mágico | Túnica Arcana | ✨ | +2 ATQ, +3 PV máx |
| Épico | Couraça de Dragão | 🐲 | +6 PV máx, +3 DEF |
| Épico | Manto Sombrio | 🌑 | +2 ATQ, +2 Movimento |
| Lendário | Armadura Titânica | 🗿 | +5 DEF, +12 PV máx |
| Lendário | Vestes do Arquimago | 🌟 | +4 ATQ, +8 PV máx |

## Mãos (10 itens)

| Raridade | Nome | Ícone | Efeito |
|---|---|---|---|
| Comum | Luvas de Couro | 🧤 | +1 ATQ |
| Comum | Manoplas Simples | 👊 | +1 DEF |
| Raro | Luvas Reforçadas | 🧤 | +2 ATQ |
| Raro | Manoplas de Ferro | 👊 | +2 DEF, −1 Movimento |
| Mágico | Luvas da Precisão | 🎯 | +1 ATQ, Crítico com 19+ |
| Mágico | Manoplas Rúnicas | 🔸 | +2 DEF, +2 ATQ |
| Épico | Luvas do Assassino | 🗡️ | +3 ATQ, +1 Movimento |
| Épico | Manoplas do Titã | 💪 | +4 dano, +2 DEF |
| Lendário | Luvas do Vento Cortante | 🌪️ | +4 ATQ, +2 Movimento, Crítico com 18+ |
| Lendário | Manoplas do Juízo | ⚖️ | +3 ATQ, +3 DEF, +6 dano |

## Pés (10 itens)

| Raridade | Nome | Ícone | Efeito |
|---|---|---|---|
| Comum | Bota Surrada | 👢 | +1 Movimento |
| Comum | Sandálias de Couro | 🩴 | +1 DEF |
| Raro | Bota Élfica | 👢 | +1 Movimento, +1 DEF |
| Raro | Botas do Corredor | 👟 | +2 Movimento |
| Mágico | Botas Élficas Reais | 🍃 | +2 Movimento, +1 DEF |
| Mágico | Grevas de Ferro | ⚙️ | +3 DEF, −1 Movimento |
| Épico | Botas do Vento | 🌬️ | +2 Movimento, +1 Alcance |
| Épico | Grevas do Campeão | 🏆 | +3 DEF, +4 PV máx |
| Lendário | Botas do Vento Norte | ❄️ | +3 Movimento, +2 Alcance |
| Lendário | Grevas Eternas | ♾️ | +5 DEF, +8 PV máx, +1 Movimento |

## Acessório (16 itens)

| Raridade | Nome | Ícone | Efeito |
|---|---|---|---|
| Comum | Anel de Couro | 💍 | +2 PV máx |
| Comum | Pingente Sem Graça | 📿 | +1 DEF |
| Comum | Bracelete de Latão | 📿 | +1 Movimento |
| Raro | Anel de Vigor | 💍 | +4 PV máx |
| Raro | Anel do Foco | 💍 | +1 ATQ, +1 DEF |
| Raro | Amuleto do Viajante | 📿 | +2 Movimento |
| Mágico | Amuleto da Sorte | 🍀 | Crítico com 19+ |
| Mágico | Pedra do Poder | 💎 | +2 ATQ, +2 DEF |
| Mágico | Colar dos Videntes | 🔮 | +3 pra achar segredos, +1 Alcance |
| Épico | Coração de Titã | ❤️ | +10 PV máx, +2 DEF |
| Épico | Anel do Destino | 💫 | Crítico com 18+, +1 ATQ |
| Épico | Anel da Fera | 💍 | +3 ATQ, +1 Movimento |
| Épico | Talismã do Guardião | 🧿 | +3 DEF, +6 PV máx |
| Lendário | Relíquia do Caos | 🌀 | +4 ATQ, +4 DEF, Crítico com 18+ |
| Lendário | Anel da Eternidade | 💍 | +14 PV máx, +2 DEF |
| Lendário | Coração de Fênix | 🔥 | +4 ATQ, Crítico com 18+, +1 Alcance |

