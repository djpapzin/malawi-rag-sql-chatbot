#!/bin/bash
source /home/dj/miniconda/etc/profile.d/conda.sh
conda activate malawi-rag-sql-chatbot

# Log environment variables for debugging
echo "Environment variables at startup:" > /tmp/malawi-env-debug.log
echo "TOGETHER_API_KEY=${TOGETHER_API_KEY:0:5}..." >> /tmp/malawi-env-debug.log
echo "LOG_LEVEL=$LOG_LEVEL" >> /tmp/malawi-env-debug.log
echo "LLM_MODEL=$LLM_MODEL" >> /tmp/malawi-env-debug.log
echo "LLM_TEMPERATURE=$LLM_TEMPERATURE" >> /tmp/malawi-env-debug.log

# Only set environment variables if they're not already set
[ -z "$TOGETHER_API_KEY" ] && export TOGETHER_API_KEY=tgp_v1_Szc4dceAlkTgtP-_rrcsoFKRO3Q-UCWJIS6jczCalj4
[ -z "$LOG_LEVEL" ] && export LOG_LEVEL=DEBUG
[ -z "$LLM_MODEL" ] && export LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
[ -z "$LLM_TEMPERATURE" ] && export LLM_TEMPERATURE=0.1

# Log environment variables after potential updates
echo "Environment variables after updates:" >> /tmp/malawi-env-debug.log
echo "TOGETHER_API_KEY=${TOGETHER_API_KEY:0:5}..." >> /tmp/malawi-env-debug.log
echo "LOG_LEVEL=$LOG_LEVEL" >> /tmp/malawi-env-debug.log
echo "LLM_MODEL=$LLM_MODEL" >> /tmp/malawi-env-debug.log
echo "LLM_TEMPERATURE=$LLM_TEMPERATURE" >> /tmp/malawi-env-debug.log

kill -9 $(lsof -t -i:5000) 2>/dev/null || true
exec uvicorn app.main:app --host 0.0.0.0 --port 5000 --root-path /api/rag-sql-chatbot
