# Preview do protótipo

Degrau 2 da escada de `prototipar-frontend`. Use quando o alvo não tem jeito próprio de rodar o frontend, ou tem e o toolchain não está instalado nesta máquina.

```sh
SLE_PREVIEW_DIR=<caminho do protótipo> docker compose up
```

A tela sobe em `http://localhost:8173`. Colidiu com algo do alvo:

```sh
SLE_PREVIEW_PORT=8174 SLE_PREVIEW_DIR=<caminho> docker compose up
```

## O que ele não faz

Não compila, não instala dependência, não pressupõe framework. Ele serve o diretório montado e nada mais.

Isso não é limitação: é o insumo de construção. Saber que a tela vai subir sem build determina o que se escreve desde a primeira linha — HTML abrível direto, com o CSS e o JS que ele mesmo carrega. Protótipo que precisa de build para abrir chega aqui e não abre.

## Sem docker

Não bloqueia. Registre no resíduo que a tela não foi servida, e siga — o resíduo continua sendo a entrega.
