build-image:
	docker build -t tcc-simulation-env .

run-sh:
	docker run --rm -ti tcc-simulation-env sh