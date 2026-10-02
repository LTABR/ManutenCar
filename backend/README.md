# ManutenCar API

This backend uses FastAPI, SQLAlchemy, and MySQL. It is compatible with the frontend's encrypted login request and JWT client in `src/api`.

## Local setup

1. Create a MySQL database with `schema.sql` (or let the development startup hook create the tables).
2. Create a virtual environment and install `requirements.txt`.
3. Copy `.env.example` to `.env` and set `DATABASE_URL`, `JWT_SECRET`, and `AUTH_PRIVATE_KEY_PATH`.
4. Generate an RSA key pair (`openssl genpkey -algorithm RSA -out backend/secrets/auth-private-key.pem -pkeyopt rsa_keygen_bits:2048` and `openssl rsa -pubout -in backend/secrets/auth-private-key.pem -out backend/secrets/auth-public-key.pem`). Keep the private key only on the backend, and put the public PEM in the frontend's `VITE_AUTH_PUBLIC_KEY`.
5. Create a user: `python backend/scripts/create_user.py you@example.com 'a-long-password'`.
6. Run: `uvicorn app.main:app --app-dir backend --reload`.

The API is mounted at `/api`; login is `POST /api/auth/login`. The encrypted body is hybrid RSA-OAEP-256 + AES-256-GCM (`algorithm`, `encryptedKey`, `iv`, `ciphertext`).

`owners_ids` and `parts_ids` are JSON ID arrays as requested. For larger deployments, replace the JSON ownership/parts arrays with junction tables and add Alembic migrations.
