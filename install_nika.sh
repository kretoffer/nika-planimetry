#!/usr/bin/env bash

./scripts/install_cxx_problem_solver.sh

./scripts/start.sh build_kb

cd sc-web
./scripts/install_dependencies.sh
npm run build
cd ..

python3 -m venv problem-solver/py/.venv
source problem-solver/py/.venv/bin/activate
pip3 install -r problem-solver/py/requirements.txt

cd interface
npm install
npm run build
