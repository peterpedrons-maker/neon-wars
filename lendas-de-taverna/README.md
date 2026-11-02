> **Hearthblade agora é o jogo de ação.** Esta pasta é o app instalável: `index.html` leva ao jogo de ação em `mmo/` (mesmo escopo, mesma identidade `./?app=hearthblade`), e `manifest.json`/`sw.js` descrevem esse app.
> O jogo tático original foi preservado em `tatico.html` (e os ícones antigos em `assets/icons/tatico-*.png`); todos os packs, imagens e documentos continuam aqui.

# Hearthblade

RPG tático de grupo (estilo auto-battler) em um único arquivo HTML
autocontido — sem build, sem dependências locais. Usa Three.js e GSAP
via CDN, e roda direto no navegador.

## Rodar localmente

```sh
cd lendas-de-taverna
python3 -m http.server 8080
# abra http://localhost:8080/
```

## Publicado em

https://peterpedrons-maker.github.io/neon-wars/lendas-de-taverna/

(Faz parte do deploy do repositório `neon-wars` — ver `.github/workflows/deploy-pages.yml`.)

## Documentação

- [`DESIGN.md`](DESIGN.md) — decisões de design, sistemas implementados e roadmap.
- [`EQUIPAMENTOS.md`](EQUIPAMENTOS.md) — catálogo completo de itens do jogo.
