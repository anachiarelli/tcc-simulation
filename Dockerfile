FROM ubuntu:24.04

RUN apt update && apt upgrade -y
RUN apt install g++ build-essential cmake libgl1-mesa-dev libboost-dev -y
RUN mkdir -p /root/simulation

WORKDIR /root/simulation
