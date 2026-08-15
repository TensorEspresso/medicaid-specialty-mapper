#!/bin/bash
cd /Users/andy/projects/medicaid-specialty-mapper
nohup python3 -m uvicorn demo.main:app --host 0.0.0.0 --port 8645 > /tmp/demo-server.log 2>&1 &
echo "PID: $!"
sleep 2
curl -s http://localhost:8645/api/map -o /dev/null -w "Server up: HTTP %{http_code}\n"
