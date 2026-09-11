# PramaanAI

**Proof, not just a score.**

PramaanAI is an evidence-driven bidder verification platform for public procurement. Instead of
handing a procurement officer a black-box compliance score, every result traces back to
**Requirement → Evidence → Verification → Rule → Result → Confidence → Human Action** — so the
officer can see exactly where a number came from before they act on it.

This repository is a complete, runnable prototype: a FastAPI backend, a React frontend, mock
government connectors, a deterministic compliance/evidence engine, and a seeded demo tender with
five fictional bidders covering every core scenario (clean pass, a GSTIN mismatch, an expiring OEM
authorization, a missing local-content declaration, and a debarment flag).

---

## 1. Product overview

| Concept | What it means here |
|---|---|
| **Evidence Chain** | Every compliance result is a `ComplianceResult` row linking a requirement to the document it came from, the mock government record it was checked against, the rule that fired, a confidence score, and the human action taken on it. |
| **Human-in-the-loop** | AI never finalizes qualification. A mandatory failure always renders as `NOT QUALIFIED — PENDING OFFICER REVIEW`, regardless of numeric score. Officers approve, reject, override (with a reason), request clarification, mark false positive, or escalate — every action is audited. |
| **Mock government connectors** | GSTN, PAN, Udyam, MCA21, EPFO/ESIC, DPIIT/Startup India, NSIC, DigiLocker, and the debarment registry are all simulated behind one normalized interface. Swapping in a real, authorized integration later means implementing the same interface — the rules engine never changes. |
| **AI safety** | AI can classify, extract, match, and summarize — never invent evidence. Document text is always treated as data, never as instructions (prompt-injection defense). Low-confidence results fall through to manual review. |

---

## 2. Architecture

```
pramaanai/
├── api/                        # FastAPI backend
│   ├── main.py                 # app entrypoint, router registration
│   ├── config.py               # pydantic-settings configuration
│   ├── deps.py                 # auth/RBAC dependencies
│   ├── auth/                   # users, roles, JWT login, RBAC permission map
│   ├── tenders/                # tenders, requirements, bidders, submissions
│   ├── documents/               # upload pipeline, extraction registry
│   │   └── extractors/
│   ├── connectors/              # normalized mock government API registry
│   ├── compliance/              # rules engine, scoring, evidence chain, extraction
│   ├── audit/                   # append-only audit log
│   ├── analytics/, alerts/, search/
│   ├── seed/                    # demo data seed script
│   └── db/
│       ├── session.py
│       └── migrations/          # Alembic
│
└── web/                         # React (Vite) frontend
    └── src/
        ├── pages/                # Login, Dashboard, Tenders, Compliance Matrix, etc.
        ├── components/           # Sidebar, TopBar, EvidenceViewer, shared UI primitives
        ├── context/              # auth context
        └── lib/                  # API client
```

**Backend:** Python, FastAPI, SQLAlchemy, Alembic, JWT auth, RBAC.
**Frontend:** React 19, Vite, Tailwind CSS v4, React Router, Recharts, lucide-react.
**Database:** SQLite by default (zero setup); Postgres via Docker Compose for a production-like path.

---

## 3. Quick start (no Docker — fastest path)

### Backend
```bash
cd pramaanai
python3 -m venv .venv && source .venv/bin/activate      # optional but recommended
pip install fastapi "uvicorn[standard]" sqlalchemy pydantic pydantic-settings \
            "python-jose[cryptography]" "passlib[bcrypt]" "bcrypt==4.0.1" \
            python-multipart alembic psycopg2-binary email-validator

cp .env.example .env                 # defaults already work for SQLite

python -m alembic upgrade head       # creates pramaanai.db with the full schema
python -m api.seed.seed              # seeds demo users, CPCL Demo Tender 2026, 5 bidders

uvicorn api.main:app --reload --port 8000
```
API is now at `http://localhost:8000` (interactive docs at `/docs`).

### Frontend
```bash
cd pramaanai/web
npm install
npm run dev
```
App is now at `http://localhost:5173` (Vite proxies `/api/*` to the backend on port 8000).

> Note: `passlib` requires `bcrypt==4.0.1` specifically — newer `bcrypt` releases changed an
> internal API `passlib` 1.7.4 depends on.

---

## 4. Quick start (Docker Compose — Postgres-backed)

```bash
cd pramaanai
cp .env.example .env
docker compose up --build
```
This starts Postgres, runs Alembic migrations, seeds the demo data, and starts both the API
(`:8000`) and frontend (`:5173`) containers.

---

## 5. Demo credentials

All accounts share the password **`Pramaan@2026`**. The login page also has a **"Demo access"**
panel that fills these in for you.

| Role | Email |
|---|---|
| Procurement Officer | `procurement.officer@pramaanai.gov.in` |
| Procurement Administrator | `procurement.admin@pramaanai.gov.in` |
| Compliance Reviewer | `compliance.reviewer@pramaanai.gov.in` |
| Department Administrator | `department.admin@pramaanai.gov.in` |
| Audit Officer | `audit.officer@pramaanai.gov.in` |
| Senior Approving Authority | `approving.authority@pramaanai.gov.in` |

---

## 6. The demo flow (judge / evaluator script)

1. **Log in** as the Procurement Officer.
2. **Dashboard** → see the CPCL Demo Tender 2026 under evaluation, KPIs, and risk alerts.
3. Open **CPCL/2026/DEMO/001** → see 8 confirmed requirements and 5 bidder submissions.
4. Open **ABC Industrial Systems Pvt Ltd** → Compliance Passport shows `87.5%`, **HIGH RISK**,
   status `NOT QUALIFIED — PENDING OFFICER REVIEW`.
5. In the **Compliance Matrix**, click the **"Valid & Matching GSTIN"** row (status: `Mismatch`).
6. The **Evidence Viewer** opens: document value `33ABCDE1234F1Z5` vs. portal value
   `33ABCDE1234F1Z6`, the differing character highlighted, 99% confidence, HIGH risk, the exact
   rule that fired, and plain-language reasons.
7. Click **Request Clarification** (or **Override**, with a reason).
8. Go to **Audit Trail** → see the action logged immutably with actor, timestamp, and reason.
9. Return to the matrix — the row now shows as resolved.

Other seeded scenarios to explore: **Bharat Equipment Solutions** (OEM authorization expiring in
18 days), **National Engineering Supplies** (missing local-content declaration), **Secure
Industrial Systems** (flagged in the mock debarment registry).

---

## 7. API overview

All endpoints are namespaced and documented via FastAPI's auto-generated OpenAPI docs at
`/docs`. Key groups:

- `POST /auth/login`, `GET /auth/me`
- `GET/POST /tenders`, `POST /tenders/{id}/requirements/extract`, `POST /tenders/{id}/requirements/confirm`
- `POST /documents/upload`, `GET /documents/submission/{id}`
- `GET /compliance/submission/{id}/matrix`, `GET /compliance/results/{id}/evidence`,
  `POST /compliance/results/{id}/action/{approve|reject|override|request_clarification|mark_false_positive|escalate}`
- `GET /audit`, `GET /analytics/overview`, `GET /alerts`, `GET /search`

## 8. Mock government integrations

`api/connectors/registry.py` is the single swap point between mock and real integrations. Every
connector (GSTN, PAN, Udyam, MCA21, EPFO/ESIC, Startup India, NSIC, DigiLocker, debarment) is
built to the same `Connector.lookup(identifier) -> ConnectorResponse` interface
(`api/connectors/base.py`). None of these call live government systems — they return
deterministic fictional data seeded in `api/connectors/mock.py`.

## 9. Security

Implemented for this MVP: JWT authentication, bcrypt password hashing, per-role RBAC enforced at
the route layer, file type/size validation on uploads, environment-based secrets, structured audit
logging, and role-scoped data access. **Not implemented** (do not claim in a production pitch
without adding them): rate limiting, virus/malware scanning of uploads, encryption at rest, SSO,
and a certified security audit.

## 10. Privacy

Only the data required for verification is collected. Auditors have read-only access everywhere;
all other roles are scoped by the RBAC permission map in `api/auth/rbac.py`. Sensitive documents
are never sent to any general-purpose external AI API — extraction in this prototype runs on
deterministic, seeded logic (see `api/documents/extractors/registry.py`), and the architecture
(`document → extraction → structured field → validation → compliance reasoning`) keeps document
text from ever being treated as an instruction.

## 11. AI safety

- AI cannot create evidence — every fact traces to an uploaded document or a connector response.
- A numeric compliance score can never override a mandatory requirement failure.
- Low-confidence or ambiguous results always route to manual review, never auto-approval.

## 12. Production evolution

To move this from prototype to production: swap SQLite for Postgres (already wired via
`DATABASE_URL` + Alembic), replace mock connectors with authorized government API integrations one
at a time behind the existing `Connector` interface, replace the deterministic document extractors
with a real OCR/layout-understanding pipeline, add virus scanning and antivirus quarantine to the
upload pipeline, add rate limiting and a WAF, and add SSO/MFA for government user accounts.
