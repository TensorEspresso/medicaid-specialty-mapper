#!/bin/bash
cd /Users/andy/projects/medicaid-specialty-mapper
python3 -m uvicorn demo.main:app --host 0.0.0.0 --port 8645
