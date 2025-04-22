build-image:
	docker build -t tcc-simulation-env .

run-sh:
	docker run --rm -ti -v ./:/root/simulation tcc-simulation-env bash

build:
	docker run --rm -ti -v ./:/root/simulation tcc-simulation-env cmake src/ -B build

build-test-simulation:
	make build
	docker run --rm -ti -v ./:/root/simulation --workdir /root/simulation/build/test_simulation tcc-simulation-env make

run-test-simulation:
	make build-test-simulation
	docker run --rm -ti -v ./:/root/simulation --workdir /root/simulation/build/test_simulation tcc-simulation-env ./simulation

clear-build:
	docker run --rm -ti -v ./:/root/simulation tcc-simulation-env rm -fr build
