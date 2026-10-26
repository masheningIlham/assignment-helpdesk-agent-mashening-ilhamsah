"""
Entry point aplikasi FastAPI — IT Helpdesk Assistant.

Alur endpoint utama:
  1. Menerima pertanyaan/permintaan dari user
  2. Meneruskan ke router (router.py) untuk menentukan intent
  3. Router memanggil RAG (rag.py) atau tool (tools.py) sesuai intent
  4. Mengembalikan response terstruktur ke client
"""
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.router import handle_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI(title="IT Helpdesk Assistant API")


class AskRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="Pertanyaan atau permintaan pengguna",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Query cannot be empty or whitespace.")
        return value


class AskResponse(BaseModel):
    status: str
    intent: str
    data: str


@app.get("/health")
async def health():
    """Endpoint sederhana untuk memastikan service berjalan."""
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """
    Endpoint utama. Menerima pertanyaan bebas dari user (bisa berupa
    pertanyaan informasi/kebijakan ATAU permintaan cek status tiket),
    lalu meneruskannya ke router untuk diproses.

    # TODO: tambahkan error handling untuk kondisi LLM gagal merespons
    # atau intent tidak dapat dikenali (lihat panduan error handling di Sesi 13.4)
    """
    try:
        result = await handle_query(request.query)
        return AskResponse(**result)

    except HTTPException:
        raise

    except (TimeoutError, ConnectionError):
        logger.exception("Service dependency unavailable or timed out")
        raise HTTPException(
            status_code=503,
            detail="A required service is temporarily unavailable.",
        )

    except Exception:
        logger.exception("Unexpected error while processing query")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the request.",
        )
