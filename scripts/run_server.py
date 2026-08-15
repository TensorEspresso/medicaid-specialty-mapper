#!/usr/bin/env python3
import subprocess, sys, os
os.chdir('/Users/andy/projects/medicaid-specialty-mapper')
proc = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'demo.main:app', '--host', '0.0.0.0', '--port', '8645'])
proc.wait()
