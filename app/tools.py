"""
Modul Tools — fungsi-fungsi "aksi" yang dipanggil router ketika intent
BUKAN pertanyaan informasi/kebijakan, melainkan permintaan spesifik
yang butuh pengecekan data langsung (bukan retrieval semantik).

Pola ini mengikuti konsep Tool Integration di Sesi 12.3.
"""

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MOCK_TICKETS_PATH = "data/mock_tickets.csv"


def get_ticket_status(ticket_id: str) -> str:
    """
    Mencari status tiket berdasarkan ticket_id pada data mock_tickets.csv.

    # TODO: implementasikan pencarian data tiket berdasarkan ticket_id.
    # Jika ticket_id tidak ditemukan, kembalikan pesan yang informatif
    # (bukan error yang membuat aplikasi crash).
    #
    # Contoh langkah:
    #   1. Muat mock_tickets.csv menggunakan pandas
    #   2. Cari baris dengan ticket_id yang cocok
    #   3. Jika ditemukan, susun string jawaban (subject, status, last_update)
    #   4. Jika tidak ditemukan, kembalikan pesan bahwa tiket tidak ditemukan
    """
    if not isinstance(ticket_id, str) or not ticket_id.strip():
        return "ID tiket tidak valid."

    ticket_id = ticket_id.strip()

    try:
        df = pd.read_csv(MOCK_TICKETS_PATH, dtype={"ticket_id": "string"})
    except (pd.errors.EmptyDataError, pd.errors.ParserError, FileNotFoundError) as e:
        return f"Data tiket tidak dapat dibaca: {e}"

    ticket_ids = df["ticket_id"].str.strip()
    matches = df.loc[ticket_ids == ticket_id]

    if matches.empty:
        return (
            f"Tiket dengan ID {ticket_id} tidak ditemukan. "
            "Periksa kembali ID tiket Anda."
        )

    ticket = matches.iloc[0]

    subject = ticket["subject"]
    status = ticket["status"]
    last_update = ticket["last_update"]

    subject = (
        str(subject).strip()
        if pd.notna(subject) and str(subject).strip()
        else "Tidak tersedia"
    )
    status = (
        str(status).strip()
        if pd.notna(status) and str(status).strip()
        else "Tidak tersedia"
    )
    last_update = (
        str(last_update).strip()
        if pd.notna(last_update) and str(last_update).strip()
        else "Tidak tersedia"
    )

    return f"({subject}, {status}, {last_update})"