#!/bin/bash
source /home/dj/miniconda/etc/profile.d/conda.sh
conda activate malawi-rag-sql-chatbot
export TOGETHER_API_KEY=tgp_v1_Szc4dceAlkTgtP-_rrcsoFKRO3Q-UCWJIS6jczCalj4
export LOG_LEVEL=DEBUG
kill -9 $(lsof -t -i:5000) 2>/dev/null || true
exec uvicorn app.main:app --host 0.0.0.0 --port 5000 --root-path /api/rag-sql-chatbot
