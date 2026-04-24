#!/bin/bash
# Vercel 版本本地调试
cd "$(dirname "$0")/.."
uvicorn vercel_app.main:app --reload --port 8000 --host 0.0.0.0
