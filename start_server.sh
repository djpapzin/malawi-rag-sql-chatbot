#!/bin/bash
source /home/dj/miniconda/etc/profile.d/conda.sh
conda activate malawi-rag-sql-chatbot

# Explicitly set environment variables
export TOGETHER_API_KEY=tgp_v1_Szc4dceAlkTgtP-_rrcsoFKRO3Q-UCWJIS6jczCalj4
export LOG_LEVEL=DEBUG
export LLM_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K
export LLM_TEMPERATURE=0.1

# Log environment variables for debugging
echo "Environment variables at startup:" > /tmp/malawi-env-debug.log
echo "TOGETHER_API_KEY=${TOGETHER_API_KEY:0:5}..." >> /tmp/malawi-env-debug.log
echo "LOG_LEVEL=$LOG_LEVEL" >> /tmp/malawi-env-debug.log
echo "LLM_MODEL=$LLM_MODEL" >> /tmp/malawi-env-debug.log
echo "LLM_TEMPERATURE=$LLM_TEMPERATURE" >> /tmp/malawi-env-debug.log

# Log environment variables after potential updates
echo "Environment variables after updates:" >> /tmp/malawi-env-debug.log
echo "TOGETHER_API_KEY=${TOGETHER_API_KEY:0:5}..." >> /tmp/malawi-env-debug.log
echo "LOG_LEVEL=$LOG_LEVEL" >> /tmp/malawi-env-debug.log
echo "LLM_MODEL=$LLM_MODEL" >> /tmp/malawi-env-debug.log
echo "LLM_TEMPERATURE=$LLM_TEMPERATURE" >> /tmp/malawi-env-debug.log

kill -9 $(lsof -t -i:5000) 2>/dev/null || true
exec uvicorn app.main:app --host 0.0.0.0 --port 5000 --root-path /api/rag-sql-chatbot
