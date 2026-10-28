# IT Helpdesk Assistant — Starter Repository

Berikut adalah prototipe backend untuk People & IT Operations helpdesk assistant. API ini menggabungkan *Retrieval-Augmented Generation* (RAG) untuk kebijakan perusahaan dan pertanyaan umum (FAQ) dengan alur kerja berbasis perangkat (*tool-based workflow*) untuk pengecekan langsung status tiket.

## 1. Problem Statement

Karyawan sering menanyakan pertanyaan repetitif kepada tim People & IT Operations mengenai kebijakan perusahaan dan prosedur spesifik pengecekan status tiket. Tim ingin membangun sebuah asisten AI internal yang dapat menangani kedua jenis permintaan tersebut secara otomatis dalam satu sistem yang sama. Cara kerja dari sistem ini adalah:

- **Pertanyaan Kebijakan** akan dijawab menggunakan knowledge base.
- **Pengecekan Status Tiket** akan menggunakan sistem pencarian deterministik, bukan semantic search.
- **Out-of-scope** Pertanyaan di luar kedua konteks di atas tidak akan dijawab oleh sistem.

Projek ini menggunakan endpoint FastAPI `POST /ask`.

## 2. Struktur Project

```
it-helpdesk-assignment/
├── app/
│   ├── main.py     # Entry point FastAPI, berisi endpoint /ask
│   ├── router.py   # Intent detection + routing ke RAG atau tool call
│   ├── rag.py      # Modul RAG: embedding, FAISS, semantic search, LLM answer
│   └── tools.py    # Modul tool call: pengecekan status tiket
├── data/
│   ├── it_helpdesk_knowledge_base.csv
│   └── mock_tickets.csv
├── Dockerfile
├── .env.example
├── requirements.txt
└── README.md  
```

## 3. Workflow Design

```
Client
  |
  | POST /ask {"query": "..."}
  v
FastAPI endpoint (app/main.py)
  |
  v
Intent detection dan routing (app/router.py)
  |
  +-- FAQ / knowledge question
  |      |
  |      v
  |   RAG pipeline (app/rag.py)
  |      1. Query embedding
  |      2. Semantic search menggunakan FAISS index untuk mendapakan knowldedge-base yang relevan
  |      3. Menggunakan knowledge-base yang didapat sebagai konteks untuk menjawab query
  |      4. Sistem akan menjawab tidak memiliki informasi jika pertanyaan di luar konteks penggunaan helpdesk assistant
  |
  +-- Ticket-status request
         |
         v
      Tool call (app/tools.py)
         1. Extract ticket ID
         2. Look up di data/mock_tickets.csv
         3. Menampilkan status ticket
  |
  v
JSON response: status, intent, data
```

## 4. Menjalankan Secara Lokal (tanpa Docker)

```bash
pip install -r requirements.txt
cp .env.example .env   # lalu isi GEMINI_API_KEY di dalam .env
uvicorn app.main:app --reload
```

## 5. Menjalankan dengan Docker

```bash
docker build -t it-helpdesk-assistant .
docker run -p 8000:8000 --env-file .env it-helpdesk-assistant
```

## 6. Menguji Endpoint

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "berapa jatah cuti tahunan saya?"}'
```

## 7. Contoh Pengujian

### Test 1 — Internal system access

**Request**

```json
{
  "query": "cara memperoleh akses ke sistem internal terbaru?"
}
```

**Observed response — HTTP 200**

```json
{
  "status": "success",
  "intent": "faq",
  "data": "Untuk memperoleh akses ke sistem internal terbaru, silakan ikuti prosedur berikut:\n\n1. Ajukan permohonan akses melalui tiket IT.\n2. Pastikan permohonan tersebut mendapatkan persetujuan dari atasan Anda.\n\nProses ini biasanya membutuhkan waktu 1-2 hari kerja untuk diselesaikan."
}
```

**Assessment:** Router memilih `faq` sebagai intent, dan jawaban sesuai dengan pertanyaan.

### Test 2 — Work laptop is unusable

**Request**

```json
{
  "query": "Laptop kerja saya tidak bisa dipakai, saya harus bagaimana?"
}
```

**Observed response — HTTP 200**

```json
{
  "status": "success",
  "intent": "faq",
  "data": "Jika laptop kerja Anda tidak bisa dipakai karena rusak, silakan ikuti langkah-langkah berikut:\n\n1. Laporkan kerusakan tersebut melalui tiket IT dengan memilih kategori 'Hardware Issue'.\n2. Sertakan deskripsi masalah yang dialami agar tim IT dapat memberikan unit pengganti sementara jika diperlukan."
}
```

**Assessment:** Router dengan tepat menentukan intent sebagai `faq`, dan jawaban sudah sesuai.

### Test 3 — Existing ticket

**Request**

```json
{
  "query": "Saya ingin tahu status tiket TICKET-0010"
}
```

**Observed response — HTTP 200**

```json
{
  "status": "success",
  "intent": "ticket_status",
  "data": "(Laptop overheat saat dipakai lama, Diproses, 2026-08-27)"
}
```

**Assessment:** Router memilih intent `ticket_status`, dan status tiket dapat ditampilkan.

### Test 4 — Ticket ID not found

**Request**

```json
{
  "query": "Cek tiket TICKET-0067"
}
```

**Observed response — HTTP 200**

```json
{
  "status": "success",
  "intent": "ticket_status",
  "data": "Tiket dengan ID TICKET-0067 tidak ditemukan. Periksa kembali ID tiket Anda."
}
```

**Assessment:** Router sudah benar memilih intent, tetapi karena di data tidak ada tiket dengan ID 0067 maka sistem akan menjawab tiket tidak ditemukan.

### Test 5 — Out-of-scope question

**Request**

```json
{
  "query": "buatlah jokes pinggir jurang terkait kondisi pemerintahan Indonesia sekarang"
}
```

**Observed response — HTTP 200**

```json
{
  "status": "success",
  "intent": "faq",
  "data": "Mohon maaf, saya tidak memiliki informasi yang cukup dari *knowledge base* untuk menjawab pertanyaan Anda mengenai kondisi pemerintahan Indonesia. Sebagai *helpdesk assistant* untuk tim People & IT Operations, tugas saya terbatas pada memberikan informasi terkait kebijakan dan prosedur perusahaan yang tersedia dalam dokumen referensi saya."
}
```

**Assessment:** Router sudah benar dalam pemilihan intent, tetapi karena pertanyaan yang diajukan di luar konteks penggunakan maka sistem akan menjawab tidak tahu.

## 8. Keterbatasan Sistem

1. **Retrieval dan jawaban tidak dijamin benar.** Semantic search dapat menghasilkan konteks yang kurang tepat dan LLM bisa menyalah artikan pertanyaan atau konteks.
2. **Pencarian tiket bergantung pada ekstraksi ID tiket.** Typo pada ID tiket akan menyebabkan sistem tidak bisa menemukan tiket yang dimaksud.
3. **External API dependency.** Embedding dan answer generation menggunakan Gemini API yang mana memiliki kuota sehingga dapat terkena limit. Selain itu, latensi dan error dari provider Gemini dapat memengaruhi response yang diberikan.
