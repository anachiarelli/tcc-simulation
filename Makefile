build-image:
	docker build -t tcc-simulation-env .

run-sh:
	docker run --rm -ti -v ./:/root/simulation tcc-simulation-env bash

build:
	docker run --rm -ti -v ./:/root/simulation tcc-simulation-env cmake src/ -B build

build-simulation: build
	docker run --rm -ti -v ./:/root/simulation --workdir /root/simulation/build/simulations/$(simulation) tcc-simulation-env make

run: build-simulation
	docker run --rm -ti -v ./:/root/simulation --workdir /root/simulation/build/simulations/$(simulation) tcc-simulation-env ./$(simulation)

clear-build:
	docker run --rm -ti -v ./:/root/simulation tcc-simulation-env rm -fr build



build-test:
	docker run --rm -ti -v ./:/root/simulation tcc-simulation-env cmake test_src/ -B build_test
	docker run --rm -ti -v ./:/root/simulation --workdir /root/simulation/build_test/ tcc-simulation-env make

run-test: build-test
	docker run --rm -ti -v ./:/root/simulation --workdir /root/simulation/ tcc-simulation-env ./build_test/load_input
