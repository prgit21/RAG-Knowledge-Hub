# Microfrontend Knowledge Hub (WIP)

## Overview

A multi-framework microfrontend application built with **single-spa**, integrating Angular and React frontends with a **FastAPI** backend. This project evolves into a **Knowledge Hub / Research Assistant**: users upload documents (PDFs, lecture notes, articles) and query them conversationally, with results powered by a Retrieval-Augmented Generation (RAG) pipeline.

---

## Architecture

### Frontend (Microfrontends)

* **Root Config**: `app-root-config.ts` + `microfrontend-layout.html` handle routing and application registration.
* **Routes**:

  * `/` → Login (Angular)
  * `/dashboard` → Dashboard (Angular)
  * `/ask` → Ask UI (React, query interface)
  * `/admin` → Admin UI (Angular, upload & ingestion status)
* **Import Map**: `importmap.json` resolves module URLs for each microfrontend.

### Backend (FastAPI)

* **Auth**: JWT-based login (`/api/login`) and protected routes (`/api/protected`).
* **Knowledge Hub Endpoints**:

  * `/api/documents` → Upload/list documents (stored in MinIO/S3).
  * `/api/ingest` → Worker ingestion (parse → chunk → embed → pgvector).
  * `/api/ask` → Conversational Q\&A endpoint (retrieves from pgvector, caches in Redis, calls LLM).

### Data Services

* **Postgres + pgvector**: Store chunks + embeddings.
* **Redis**: Cache answers, queue tasks.
* **MinIO/S3**: Store uploaded documents.

---

## Knowledge Hub / Research Assistant

### What it is

A platform for uploading and querying academic or reference materials conversationally.


* Demonstrates an **end-to-end ingestion pipeline** (Admin MF → FastAPI → MinIO → Worker → Postgres/pgvector).
* Implements **RAG retrieval** (vector DB + Redis cache).
* Highlights **microfrontend separation**:

  * **Ask MF**: end-users query content.
  * **Admin MF**: admins upload and monitor ingestion.
* **Stretch Goals**:

  * Per-course RBAC (students vs instructors).
  * Hybrid retrieval (BM25 + vectors).
  * Evaluation harness for retrieval quality.

---

## Development Workflow

### Install dependencies

* **Frontends**: `npm install` at the root and inside each MF (`angular-app`, `dashboard`, `react-app`, `ask-app`, `admin-app`).
* **Backend**: `pip install -r requirements.txt` in `python-backend`, configure `.env` with JWT + DB/Redis/MinIO credentials.

### Run locally

* `./start-servers.sh` launches root config, Angular apps, React apps, and FastAPI backend.
* Root shell: [http://localhost:9000](http://localhost:9000)
* Ask UI: `/ask`
* Admin UI: `/admin`

### Run with Docker

* `docker-compose up --build` starts all services. Ports:

  * root: 9000
  * login: 4201
  * dashboard: 4200
  * ask: 3001
  * admin: 3002
  * backend: 8000
  * postgres: 5432
  * redis: 6379
  * minio: 9000 (console 9001)

---

## Status

This is an active **work in progress**. Current capabilities include:

* JWT authentication and protected routes.
* Microfrontends integrated via single-spa.
* RAG pipeline under development (document upload, ingestion, and query flow).

Future iterations will expand retrieval quality, RBAC, observability,RAG completion and CI/CD integration.
