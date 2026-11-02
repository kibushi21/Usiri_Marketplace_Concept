# Usiri Marketplace — working application

A running implementation of the Usiri marketplace blueprint: a managed, multi-supplier
marketplace for Tanzanian homes with a customer storefront, a supplier portal and an
operations console.

This is a **demonstration build**. Payments and deliveries are simulated behind the same
interfaces a licensed PSP and a real carrier would use. No real money moves and no real
supplier, customer or logistics data is involved.

The requirements, decision log and SRS behind this build live in
[`../Software_Blueprint`](../Software_Blueprint). The application implements decisions
D-01 to D-04 from that pack: six bounded general-merchandise departments, supplier-held
stock with licensed carriers, a licensed PSP with post-delivery supplier payout, and a
custom modular monolith (Next.js/TypeScript, FastAPI, PostgreSQL in production).

## Layout

```
Application/
├── backend/                  FastAPI API, domain services, tests
│   ├── app/
│   │   ├── api/              HTTP routers (auth, catalogue, cart, orders, returns,
│   │   │                     support, supplier, ops)
│   │   ├── services/         pricing, inventory, payments, ledger, refunds, returns,
│   │   │                     payouts, supplier orders, audit, config, notifications
│   │   ├── adapters/         PSP, carrier and vision provider boundaries (mock implementations)
│   │   ├── models.py         SQLAlchemy schema
│   │   ├── seed.py           demo departments, suppliers, products, accounts
│   │   └── cli.py            init-db / seed / reset commands
│   ├── tests/                money, checkout, pricing and access-control tests
│   └── var/usiri.db          development SQLite database (created on first run)
└── web/                      Next.js 16 App Router frontend
    └── src/
        ├── app/(store)/      storefront, cart, checkout, orders, support,
        │                     supplier portal, operations console
        ├── app/pay/          mock PSP payment page
        ├── components/       UI and portal panels
        └── lib/              API client, auth, formatting, types
```

## Prerequisites

- Python 3.11 or newer (built and tested on 3.14)
- Node.js 20 or newer (tested on 24)
- pnpm through Corepack (`corepack pnpm …`); there is no global `npm` binary required
- No database server is needed for local development — the backend uses SQLite

## Run the backend

```bash
cd Application/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

On startup in development the API creates the schema if needed and seeds demo data. Open
<http://localhost:8000/docs> for the interactive API documentation, or
<http://localhost:8000/api/health> for a health check.

Maintenance commands:

```bash
.venv/bin/python -m app.cli reset     # drop, recreate and reseed the database
.venv/bin/python -m app.cli seed      # seed without dropping existing rows
.venv/bin/python -m app.cli init-db   # create tables only
```

The development database is `backend/var/usiri.db`. Deleting that file and restarting is
also a clean reset.

## Run the web app

```bash
cd Application/web
corepack pnpm install
cp .env.example .env.local
corepack pnpm dev
```

Open <http://localhost:3000>. `NEXT_PUBLIC_API_URL` must point at the API and include
`/api`; the default is `http://localhost:8000/api`. The backend allows
`http://localhost:3000` by default through `USIRI_CORS_ORIGINS`.

Production build:

```bash
corepack pnpm build
corepack pnpm start
```

## Demo accounts

Every seeded account uses the password **`Usiri#2026`**. The login page also offers
one-click buttons for these accounts.

| Interface | Email | Name | Role |
| --- | --- | --- | --- |
| Customer | `demo@usiri.co.tz` | Asha Juma | customer |
| Customer | `daniel@example.co.tz` | Daniel Kimaro | customer |
| Supplier | `kariakoo@suppliers.usiri.co.tz` | Kariakoo Homeware | supplier |
| Supplier | `mwanga@suppliers.usiri.co.tz` | Mwanga Appliances | supplier |
| Supplier | `sanaa@suppliers.usiri.co.tz` | Sanaa Fashion House | supplier |
| Operations | `ops@usiri.co.tz` | Joseph Mrema | ops admin |
| Operations | `finance@usiri.co.tz` | Neema Kessy | finance — payout maker |
| Operations | `finance2@usiri.co.tz` | Zawadi Mushi | finance — payout checker |
| Operations | `support@usiri.co.tz` | Baraka Mushi | customer support |
| Operations | `admin@usiri.co.tz` | Amina Mwinyi | superadmin |

Other seeded suppliers use the same password:
`zanzibar@suppliers.usiri.co.tz`, `tumaini@suppliers.usiri.co.tz`,
`dodoma@suppliers.usiri.co.tz`, `lake@suppliers.usiri.co.tz`,
`arusha@suppliers.usiri.co.tz` and `mwanza@suppliers.usiri.co.tz`.

## What to try

1. **Checkout across suppliers.** As a customer, add products from two different
   suppliers, go to the cart and check out. The mock PSP redirects to `/pay/{payment_id}`;
   choose paid or failed. A successful payment splits the order into one supplier order
   per supplier, reserves then commits stock, and posts the double-entry ledger.
2. **Supplier fulfilment.** Sign in as a supplier, open *Orders*, accept, ship (the mock
   carrier returns a `TRK-` reference) and mark delivered. The delivery sets the payout
   eligibility date.
3. **Payouts with maker-checker.** As `finance@`, request a payout once the hold has
   elapsed; the same user cannot approve it. As `finance2@`, approve it, then execute it.
   Execution posts the provider payout, clears the supplier payable and completes the
   supplier orders.
4. **Returns.** A customer can request a return within the configured window. Operations
   decide, then receive the item — receiving refunds it in the same step; commission is
   reversed and the refund is posted to the ledger.
5. **Support.** A customer opens a ticket. Support replies publicly or adds an internal
   note — internal notes never appear in the customer's thread.
6. **Configuration.** In *Settings*, ops admins can change commission, delivery fee,
   free-delivery threshold, return window, payout hold, reservation TTL and contact
   details. Every change is written to the append-only audit trail.
7. **Search by photo.** On *Shop*, click the photo icon at the right of the search field,
   upload an image named after the product (for example `stainless-steel-kettle.png`) and
   press *Find products*. Add a hint when the file name is generic. Clear the photo search
   to return to the catalogue.
8. **Ask Usiri.** Use the chat button in the corner of the storefront or the ops console.
   Ask about delivery, returns or a product ("show me kettles"); staff also get answers
   about payouts, cargo overrides, commission and returns. The bundled assistant answers
   from the catalogue and store settings in demo mode.

## How the mock providers behave

- **Payments** are handled by `MockPaymentProvider` in `backend/app/adapters/psp.py`.
  It issues `MOCK-` references and stores status in-process. The customer-facing
  `/pay/{payment_id}` page records the simulated outcome, and a signed
  `POST /api/webhooks/psp` endpoint mirrors a real PSP callback for provider integration.
  Replace this adapter with a licensed PSP; do not extend it.
- **Carrier.** The bundled adapter is a mock courier API that issues `TRK-` references
  automatically. If the supplier supplies a tracking number instead, the shipment is
  recorded in manual mode. The adapter boundary (`app/adapters/carrier.py`) is where a
  licensed carrier is added.
- **No escrow.** Customer funds are not held by the marketplace on the customer's behalf.
  They settle through the PSP into platform clearing, and suppliers are paid after
  delivery plus the configured hold. The ledger separates PSP clearing, commission,
  delivery income and supplier payable.
- **Payout eligibility** is `delivered` (or completed) plus the hold period, with the
  eligibility timestamp fixed at the moment of delivery. Changing the hold setting does
  not retroactively move existing orders.

For a fast demo of an elapsed hold, backdate delivered orders before requesting a payout:

```bash
cd Application/backend
.venv/bin/python - <<'PY'
import sqlite3

with sqlite3.connect("var/usiri.db") as db:
    db.execute(
        "UPDATE supplier_orders SET eligible_at = datetime('now', '-1 day') "
        "WHERE status IN ('delivered', 'completed') "
        "AND payout_status = 'unpaid' AND payout_id IS NULL"
    )
PY
```

## Cargo tracking

- Each supplier order is one **cargo batch**. The customer's order page lists every
  batch with its own carrier, tracking reference and event trail, followed from dispatch
  to delivery.
- Shipments move through `booked` → `picked_up` → `in_transit` → `out_for_delivery` →
  `delivered`. The mock API carrier emits the first three milestones on a compressed
  schedule (1 second, 2 minutes and 6 minutes after dispatch). Delivery is only recorded
  by the supplier's deliver action, so payout eligibility is unchanged.
- Milestones advance on the background sweeper (every 60 seconds) and whenever a
  customer opens the order page, so the demo needs no external carrier webhook.
- Operations can override a batch from the ops order view. The endpoint
  `POST /api/ops/shipments/{id}/tracking` accepts `picked_up`, `in_transit`,
  `out_for_delivery`, `delayed`, `delivery_attempted` or `returned_to_sender` plus a
  customer-visible note. A manual override pauses simulated events for that batch;
  `delivered`, `cancelled` and `returned_to_sender` are closed to further overrides.
  Every override is written to the audit trail as `shipment.tracking_updated`.

## Search by photo

- The photo icon inside the shop search bar opens **Search by photo**. A customer uploads
  an image plus an optional short hint, and the catalogue returns products that match the
  keywords the image yields.
- `POST /api/catalogue/image-search` accepts a multipart `file` and optional `hint`
  (120 characters). JPEG, PNG, WebP and GIF are accepted up to 5 MB; the file is read in
  memory and never stored.
- The bundled `MockVisionProvider` in `backend/app/adapters/vision.py` reads keywords from
  the file name and the hint. **No image model is connected** — image pixels are not
  inspected, so a photo named `IMG_2041.jpg` only matches when a hint is supplied. The
  response carries a `note` saying so, and the UI shows it.
- Matches are scored across product name, brand, category, department, description and
  attributes, limited to active products from verified suppliers. The response returns
  `provider`, `tags`, `note`, `total` and the usual product summaries.
- To use real visual search, implement `VisionProvider.describe` (for example, an image
  embedding service that returns descriptive tags) and register it with `set_vision`.
  The API and storefront need no changes.

## Ask Usiri assistant

- The chat widget is mounted once in the storefront layout, so it is available on every
  customer page, and in the ops console for staff roles. It is hidden on the auth pages
  and the `/pay/` flow. The panel title switches between **Ask Usiri** (shopping help) and
  **Operations assistant** (internal help) based on the current path.
- `POST /api/assistant/chat` takes `{ message, history[], audience }`. `audience` is
  `customer` or `ops`; `ops` requests must carry a staff bearer token and return 401/403
  otherwise. History is capped at 8 messages and 2,000 characters, and the endpoint
  rate-limits each client to 20 requests a minute (429 beyond that).
- The assistant answers delivery, returns, tracking, payment and support questions from
  the store settings and product catalogue. Customer requests search only active products
  from verified suppliers. General questions such as "what are the best selling products
  in Tanzania" are answered honestly: the demo has no sales ranking, and the reply says so
  and lists the departments instead of inventing a ranking.
- No personal data is sent to a model. The context contains store policy values, department
  names and up to three catalogue matches; it never includes customer names, orders,
  addresses or tokens.
- The bundled `MockChatProvider` in `backend/app/adapters/assistant.py` is rule-based and
  labelled **Demo mode** in the UI, with a note that no language model is connected.
  `OpenAICompatibleProvider` calls any server exposing `/chat/completions`; it is selected
  with `USIRI_LLM_PROVIDER=openai` and reads the key from the backend environment only. The
  key is never returned to the browser or written to logs, and a provider failure returns
  503 without leaking the upstream error. Use `set_assistant` to register another provider;
  the API and UI need no changes.
- To connect a larger model, set `USIRI_LLM_PROVIDER=openai`, `USIRI_LLM_API_KEY`,
  `USIRI_LLM_MODEL` and, if needed, `USIRI_LLM_BASE_URL` (defaults to the OpenAI API;
  point it at any OpenAI-compatible gateway). Restart the backend; the UI label changes
  from **Demo mode** to the configured model name.

## Configuration

Backend settings use the `USIRI_` prefix and can be supplied as environment variables or
in `backend/.env`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `USIRI_ENVIRONMENT` | `development` | `production` disables auto-create/auto-seed |
| `USIRI_DATABASE_URL` | SQLite file in `backend/var/` | SQLAlchemy connection URL |
| `USIRI_JWT_SECRET` | dev-only placeholder | **must be set in production**; startup fails otherwise |
| `USIRI_ACCESS_TOKEN_MINUTES` | `720` | access-token lifetime |
| `USIRI_CORS_ORIGINS` | `http://localhost:3000` | comma-separated allowed origins |
| `USIRI_PSP_PROVIDER` | `mock` | reserved provider selector; the bundled adapter is mock |
| `USIRI_PSP_WEBHOOK_SECRET` | `mock-webhook-secret` | webhook signing secret |
| `USIRI_PSP_CALLBACK_BASE` | `http://localhost:8000` | base URL used in PSP redirects |
| `USIRI_CARRIER_PROVIDER` | `mock` | reserved provider selector; the bundled adapter is mock |
| `USIRI_CARRIER_MODE` | `manual` | reserved mode selector; not yet wired to adapter choice |
| `USIRI_LLM_PROVIDER` | `mock` | `mock` for rule-based answers, `openai` for an OpenAI-compatible model |
| `USIRI_LLM_BASE_URL` | `https://api.openai.com/v1` | API base for the OpenAI-compatible provider |
| `USIRI_LLM_API_KEY` | empty | server-side key; never sent to the browser |
| `USIRI_LLM_MODEL` | `gpt-4o-mini` | model name shown in the chat panel |
| `USIRI_LLM_TIMEOUT_SECONDS` | `30` | upstream request timeout |
| `USIRI_LLM_MAX_TOKENS` | `400` | reply length cap |

Business rules (commission in basis points, delivery fee, free-delivery threshold, return
window, payout hold and minimum, reservation TTL) are database-backed platform settings,
editable in the ops console and recorded in the audit trail. They are not environment
variables.

## Tests and checks

Backend:

```bash
cd Application/backend
.venv/bin/ruff check .
.venv/bin/python -m pytest -q          # 41 tests
```

Frontend:

```bash
cd Application/web
corepack pnpm typecheck
corepack pnpm build
```

## Known limitations

- Payments, payouts and tracking are mock implementations. No licensed PSP or carrier is
  integrated, and no provider credentials are configured. The `USIRI_PSP_PROVIDER`,
  `USIRI_CARRIER_PROVIDER` and `USIRI_CARRIER_MODE` settings are reserved: the running
  process always uses the bundled mock adapters.
- **Photo search** is keyword matching over file names and hints, not image recognition.
  No image model or embedding service is connected, and uploaded images are not stored.
- **Ask Usiri** runs in demo mode unless an OpenAI-compatible model is configured. The
  mock assistant matches keywords and reads store settings; it does not browse the web or
  rank products by real sales. Without an `USIRI_LLM_API_KEY` the live provider returns
  503 and the UI shows a retry message.
- There are no database migrations. The schema is created with SQLAlchemy `create_all`;
  use `app.cli reset` during development. PostgreSQL is the intended production database,
  but this build has only been exercised on SQLite.
- Notifications are recorded as in-app records; no email or SMS is sent.
- Authentication uses JWT access tokens stored in browser local storage, with no refresh
  or revocation flow. It is suitable for a demo only.
- Suppliers can create products and edit variant price, stock and active status. There
  is no staff-side catalogue administration, bulk import, search ranking, reviews or
  wishlist.
- Supplier documents are seeded references, not uploaded files.
- The blueprint documents in [`../Software_Blueprint`](../Software_Blueprint) describe
  the full intended platform. Features they mention but this build does not include —
  real provider integration, escrow alternatives, multi-warehouse fulfilment, analytics
  exports, disaster recovery — remain proposals, not implemented behaviour.
