# tcc-simulation

## Como executar

Após clonar o repositório, é necessário inicializar os submodulos utilizando `git submodule update`.

A forma mais fácil de executar esse projeto é utilizando Docker.

Para executar através do Docker, você precisa:
1. Ter o Docker instalado e executando;
1. Construir a imagem do projeto usando o comando `make build-image`
1. Executar um cenário usando o comando `make run scenario=nome_do_cenario`

---

Para executar sem utilizar o Docker, você precisará de um ambiente compatível com a configuração presente no arquivo `/Dockerfile`.

Esse projeto foi desenvolvido em ambiente Ubuntu 24.04, com os seguintes pacotes instalados:
- g++
- build-essential
- cmake
- libgl1-mesa-dev

Após a instalação das dependências:
1. Faça o _build_ do projeto: `cmake . -B build`
1. Compile o cenário: `cd /root/simulation/build/src/scenarios/[nome_do_cenario] && make`
1. Execute: `./build/src/scenarios/[nome_do_cenario]/[nome_do_executavel]`

## Notas
- Velocidade máxima do e-puck no Enki é 12.8 cm/s.
- As iterações da simulação ocorrem a cada 0.1s (apesar do e-puck só conseguir processar uma imagem a cada 0.25s).

## Referências
Especificações do E-puck: https://www.gctronic.com/doc/index.php/e-puck2