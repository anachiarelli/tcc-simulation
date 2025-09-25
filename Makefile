build-image:
	docker build -t tcc-simulation-env .

build:
	docker run --rm -ti -v ./:/root/simulation tcc-simulation-env cmake . -B build

compile: build
	docker run --rm -ti -v ./:/root/simulation --workdir /root/simulation/build/src/Scenarios/$(scenario) tcc-simulation-env make

run: compile
	docker run --rm -ti -v ./:/root/simulation --workdir /root/simulation/ tcc-simulation-env ./build/src/Scenarios/$(scenario)/$(scenario)

clear-build:
	docker run --rm -ti -v ./:/root/simulation tcc-simulation-env rm -fr build

run-sh:
	docker run --rm -ti -v ./:/root/simulation tcc-simulation-env bash
