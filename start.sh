#!/bin/bash
pip install -r backend/requirements.txt
cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT