from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
import uuid, os

load_dotenv()

import tailor, jobs, pdf_gen

OUTPUT_DIR = Path("outputs")


@asynccontextmanager
async def lifespan(app: FastAPI):
    OUTPUT_DIR.mkdir(exist_ok=True)
    yield


app = FastAPI(title="JobTailor", lifespan=lifespan)


class TailorRequest(BaseModel):
    job_description: str
    job_title: str = ""
    company: str = ""


@app.post("/api/tailor")
async def tailor_endpoint(req: TailorRequest):
    if not req.job_description.strip():
        raise HTTPException(400, "job_description is required")

    result = await tailor.tailor_resume(req.job_description, req.job_title or "", req.company or "")

    session_id = str(uuid.uuid4())[:8]
    resume_path = str(OUTPUT_DIR / f"resume_{session_id}.pdf")
    cover_path = str(OUTPUT_DIR / f"cover_{session_id}.pdf")

    await pdf_gen.html_to_pdf(result["resume_html"], resume_path)
    await pdf_gen.html_to_pdf(result["cover_letter_html"], cover_path)

    return {
        "session_id": session_id,
        "resume_url": f"/download/{session_id}/resume",
        "cover_url": f"/download/{session_id}/cover",
        "keywords": result["keywords"],
        "cover_letter_text": result["cover_letter_text"],
    }


@app.get("/api/search")
async def search_endpoint(query: str, location: str = ""):
    if not query.strip():
        raise HTTPException(400, "query is required")
    result = await jobs.search_jobs(query, location)
    result["jobs"] = _rank(result["jobs"], query)
    result["total"] = len(result["jobs"])
    return result


def _rank(job_list: list, query: str) -> list:
    """Sort jobs so exact keyword matches in title come first."""
    terms = [t.lower() for t in query.split() if t]

    def score(job):
        title = (job.get("title") or "").lower()
        desc = (job.get("description") or "").lower()
        s = 0
        for t in terms:
            if t in title:
                s += 10        # term in title = strong signal
            if title.startswith(t):
                s += 5         # title starts with search term = even stronger
            if t in desc:
                s += 1
        return s

    return sorted(job_list, key=score, reverse=True)


@app.get("/api/fetch-job")
async def fetch_job_endpoint(url: str):
    description = await jobs.fetch_job_from_url(url)
    return {"description": description}


@app.get("/download/{session_id}/{doc_type}")
async def download(session_id: str, doc_type: str):
    if doc_type not in ("resume", "cover"):
        raise HTTPException(400, "doc_type must be resume or cover")
    path = OUTPUT_DIR / f"{doc_type}_{session_id}.pdf"
    if not path.exists():
        raise HTTPException(404, "File not found — it may have expired")
    filename = "Zein_Rady_Resume.pdf" if doc_type == "resume" else "Zein_Rady_CoverLetter.pdf"
    return FileResponse(str(path), media_type="application/pdf", filename=filename)


app.mount("/", StaticFiles(directory="static", html=True), name="static")
