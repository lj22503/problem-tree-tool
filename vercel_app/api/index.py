# ─────────────────────────────────────────────────────────────────────────────
# 灵光问题树 — Vercel API  (单文件，所有路由共享内存会话)
# ─────────────────────────────────────────────────────────────────────────────
import sys
from pathlib import Path

# 让 core 模块可被导入
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core import (
    ProblemSession,
    Stage,
    SessionStore,
    create_backend,
    PromptEngine,
    WaterfallPromptEngine,
    get_available_backends,
    _BACKEND_DEFAULT_MODEL,
)

# ─────────────────────────────────────────────────────────────────────────────
# FastAPI app
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(title="灵光问题树 API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_prompt_engine = PromptEngine()
_waterfall_engine = WaterfallPromptEngine()


def _make_backend(backend: str, model: Optional[str] = None):
    try:
        return create_backend(backend)
    except (ValueError, ImportError):
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic 模型
# ─────────────────────────────────────────────────────────────────────────────
class CreateSessionReq(BaseModel):
    problem: str
    backend: str = "deepseek"
    model: Optional[str] = None


class SendMessageReq(BaseModel):
    session_id: str
    content: str
    skip_stage: bool = False


class WaterfallReq(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = None
    backend: str = "deepseek"
    model: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# 路由
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "available_backends": get_available_backends(),
        "session_count": len(SessionStore.list_all()),
    }


# ── 对话模式 ───────────────────────────────────────────────────────────────

@app.post("/api/sessions")
def create_session(req: CreateSessionReq):
    session = ProblemSession(
        problem_statement=req.problem,
        backend=req.backend,
        ai_model=req.model or _BACKEND_DEFAULT_MODEL.get(req.backend, "deepseek-chat"),
    )

    stage_prompt = _prompt_engine.get_stage_prompt(
        session.current_stage.value, req.problem
    )

    backend = _make_backend(req.backend, session.ai_model)
    if backend:
        try:
            resp = backend.generate(
                [
                    {"role": "system", "content": _prompt_engine.get_system_prompt()},
                    {"role": "user", "content": f"我的问题是: {req.problem}"},
                    {"role": "assistant", "content": stage_prompt},
                ],
                max_tokens=2000,
                model=session.ai_model,
            )
            session.add_message("assistant", resp)
        except Exception:
            session.add_message("assistant", stage_prompt)
    else:
        session.add_message("assistant", stage_prompt)

    SessionStore.save(session)
    return {"session_id": session.session_id, "session": session.to_dict()}


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    session = SessionStore.get(session_id)
    if not session:
        raise HTTPException(404, "会话不存在或已过期")
    return {"session": session.to_dict()}


@app.post("/api/sessions/{session_id}/messages")
def send_message(session_id: str, req: SendMessageReq):
    session = SessionStore.get(session_id)
    if not session:
        raise HTTPException(404, "会话不存在或已过期")
    if session.is_complete():
        raise HTTPException(400, "会话已完成，请新建会话")

    session.add_message("user", req.content)

    if req.skip_stage:
        session.advance_stage()

    backend = _make_backend(session.backend, session.ai_model)
    stage_prompt = _prompt_engine.get_stage_prompt(session.current_stage.value)

    if backend:
        try:
            messages_for_ai = [{"role": "system", "content": _prompt_engine.get_system_prompt()}]
            for m in session.messages:
                messages_for_ai.append({"role": m.role, "content": m.content})
            messages_for_ai.append({"role": "system", "content": stage_prompt})
            resp = backend.generate(messages_for_ai, max_tokens=2000, model=session.ai_model)
            session.add_message("assistant", resp)
        except Exception as e:
            session.add_message("assistant", f"抱歉，AI 响应失败: {str(e)}")
    else:
        session.add_message("assistant", "⚠️ AI 后端未配置，请检查 API 密钥。")

    SessionStore.save(session)
    return {"session": session.to_dict()}


@app.post("/api/sessions/{session_id}/advance")
def advance_stage(session_id: str):
    session = SessionStore.get(session_id)
    if not session:
        raise HTTPException(404, "会话不存在或ss过期")
    session.advance_stage()
    stage_prompt = _prompt_engine.get_stage_prompt(session.current_stage.value)
    session.add_message("assistant", stage_prompt)
    SessionStore.save(session)
    return {"session": session.to_dict()}


@app.post("/api/sessions/{session_id}/complete")
def complete_session(session_id: str):
    session = SessionStore.get(session_id)
    if not session:
        raise HTTPException(404, "会话不存在或已过期")
    session.current_stage = Stage.COMPLETED
    session.add_message("assistant", "🎉 问题树构建完成！以上是你的完整分析报告。")
    SessionStore.save(session)
    return {"session": session.to_dict()}


@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    if not SessionStore.delete(session_id):
        raise HTTPException(404, "会话不存在")
    return {"ok": True}


@app.get("/api/sessions")
def list_sessions():
    sessions = SessionStore.list_all()
    return {"sessions": [s.to_dict() for s in sessions.values()]}


# ── 瀑布模式 ───────────────────────────────────────────────────────────────

@app.post("/api/waterfall")
def waterfall(req: WaterfallReq):
    backend = _make_backend(req.backend, req.model or _BACKEND_DEFAULT_MODEL.get(req.backend))
    if not backend:
        raise HTTPException(503, "AI 后端未配置或密钥无效")

    try:
        prompt = _waterfall_engine.build_prompt(req.question, req.context)
        system = _waterfall_engine.get_system_prompt()
        result = backend.generate(
            [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            max_tokens=6000,
            temperature=0.7,
            model=req.model,
        )
        return {"result": result, "question": req.question}
    except Exception as e:
        raise HTTPException(500, f"生成失败: {str(e)}")


# ── 报告导出 ───────────────────────────────────────────────────────────────

@app.get("/api/sessions/{session_id}/report")
def get_report(session_id: str):
    session = SessionStore.get(session_id)
    if not session:
        raise HTTPException(404, "会话不存在或已过期")

    lines = [
        "# 问题树分析报告\n",
        f"## 原始问题\n{session.problem_statement}\n",
        "## 对话记录\n",
    ]
    for msg in session.messages:
        label = {"user": "👤 用户", "assistant": "🤖 AI教练"}.get(msg.role, msg.role)
        lines.append(f"### {label}\n\n{msg.content}\n")
    lines.append(f"\n---\n*报告生成时间: {session.updated_at.isoformat()}*")

    return {"report": "\n".join(lines)}
