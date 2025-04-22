build-image:
	docker build -t tcc-simulation-env .

run-sh:
	docker run --rm -ti -v ./:/root/simulation tcc-simulation-env bash

build-enki:
	docker run --rm -ti -v ./:/root/simulation tcc-simulation-env cmake enki/ -B build

build-enki-minimal:
	make build-enki
	docker run --rm -ti -v ./:/root/simulation --workdir /root/simulation/build/examples/minimal tcc-simulation-env make

run-enki-minimal:
	make build-enki-minimal
	docker run --rm -ti -v ./:/root/simulation --workdir /root/simulation/build/examples/minimal tcc-simulation-env ./enkiMinimal