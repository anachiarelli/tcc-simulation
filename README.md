# tcc-simulation

## Como executar

Após clonar o repositório, é necessário inicializar os submodulos utilizando `git submodule update`.

A forma mais fácil de executar esse projeto é utilizando Docker.

Para executar através do Docker, você precisa:
1. Ter o Docker instalado e executando;
1. Construir a imagem do projeto usando o comando `make build-image`
1. Executar um cenário usando o comando `make run scenario=nome_do_cenario`

Para interromper o experimento, execute `docker ps`, copie o CONTAINER ID e execute `docker kill {CONTAINER ID}`.

---

Pode ser necessário dar permissão de leitura e escrita para o diretório `/output`. 

## Notas
- Velocidade máxima do e-puck no Enki é 12.8 cm/s.
- As iterações da simulação ocorrem a cada 0.1s (apesar do e-puck só conseguir processar uma imagem a cada 0.25s).

## Referências
Especificações do E-puck: https://www.gctronic.com/doc/index.php/e-puck2