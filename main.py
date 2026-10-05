from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from config import APP_NAME, validate_configuration
from explanation_module import explain_topic
from learning_path import get_learning_recommendations
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title=APP_NAME,
    description=(
        "EduGenie - Google Gemini Powered Learning Assistant"
    ),
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


# ---------------------------------------------------------
# Request models
# ---------------------------------------------------------


class TextRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=15000,
    )


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )


class LearningPathRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=1,
        max_length=1000,
    )

    level: str = Field(
        default="Beginner",
        max_length=100,
    )


# ---------------------------------------------------------
# Frontend
# ---------------------------------------------------------


@app.get(
    "/",
    response_class=HTMLResponse,
)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": APP_NAME,
            "gemini_configured": validate_configuration(),
        },
    )


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "application": APP_NAME,
        "gemini_configured": validate_configuration(),
    }


# ---------------------------------------------------------
# Q&A
# ---------------------------------------------------------


@app.post("/qa")
async def qa(request: QuestionRequest):

    try:
        answer = answer_question(
            request.question
        )

        return {
            "success": True,
            "answer": answer,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ---------------------------------------------------------
# Explanation
# ---------------------------------------------------------


@app.post("/explain")
async def explain(request: TextRequest):

    try:
        explanation = explain_topic(
            request.text
        )

        return {
            "success": True,
            "explanation": explanation,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ---------------------------------------------------------
# Quiz
# ---------------------------------------------------------


@app.post("/quiz")
async def quiz(request: TextRequest):

    try:
        quiz_data = generate_quiz(
            request.text
        )

        return {
            "success": True,
            "quiz": quiz_data,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ---------------------------------------------------------
# Summarization
# ---------------------------------------------------------


@app.post("/summarize")
async def summarize(request: TextRequest):

    try:
        summary = summarize_text(
            request.text
        )

        return {
            "success": True,
            "summary": summary,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ---------------------------------------------------------
# Learning recommendations
# ---------------------------------------------------------


@app.post("/learn/recommendations")
async def learning_recommendations(
    request: LearningPathRequest,
):

    try:
        recommendations = get_learning_recommendations(
            topic=request.topic,
            level=request.level,
        )

        return {
            "success": True,
            "recommendations": recommendations,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ---------------------------------------------------------
# Run locally
# ---------------------------------------------------------


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )