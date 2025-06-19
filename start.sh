#!/usr/bin/env bash

gnome-terminal -- bash -c "./scripts/start.sh machine; exec bash"
gnome-terminal -- bash -c "./scripts/start.sh web; exec bash"
gnome-terminal -- bash -c "./scripts/start.sh py_server; exec bash"
gnome-terminal -- bash -c "./scripts/start.sh interface; exec bash"
