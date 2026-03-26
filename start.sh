#!/bin/bash
source venv/bin/activate
python3 server.py &
cd frontend && python3 -m http.server 3000 &
