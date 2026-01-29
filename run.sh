#!/bin/bash
cd /home/swind/Program/reddit-explorer
python3 do_analysis.py 2>&1 | head -200
