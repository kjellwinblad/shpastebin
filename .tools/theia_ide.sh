#!/bin/sh

# This script should be run from the root folder for the project

docker run -it --init -p 3000:3000 -v "$(pwd):/home/project" theiaide/theia-python:latest

