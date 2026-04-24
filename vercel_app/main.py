# Vercel 本地调试入口
# 本地运行: uvicorn main:app --reload --port 8000
# Vercel 部署时忽略本文件，只用 api/index.py

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vercel_app.api.index import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
