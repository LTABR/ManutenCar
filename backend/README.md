# ManutenCar API

This backend uses FastAPI, SQLAlchemy, and MySQL. It is compatible with the frontend's encrypted login request and JWT client in `src/api`.

## Local setup

1. Create a MySQL database with `schema.sql` (or let the development startup hook create the tables).
2. Create a virtual environment and install `requirements.txt`.
3. Copy `.env.example` to `.env` and set `DATABASE_URL` and a strong `JWT_SECRET`.
4. If needed, from `backend/`, generate an RSA key pair with `mkdir -p secrets && openssl genpkey -algorithm RSA -out secrets/auth-private-key.pem -pkeyopt rsa_keygen_bits:2048 && openssl pkey -in secrets/auth-private-key.pem -pubout -out secrets/auth-public-key.pem`. Set `AUTH_PRIVATE_KEY_PATH=./secrets/auth-private-key.pem` in `backend/.env`, and set the matching public PEM in the root `.env` as `VITE_AUTH_PUBLIC_KEY` (use literal `\n` between PEM lines). Never expose or commit the private key. The backend loads its `.env` and resolves the relative private-key path from the backend directory, including when started with `--app-dir backend` from the repository root.
5. Create a user: `python backend/scripts/create_user.py you@example.com 'a-long-password'`.
6. Run: `uvicorn app.main:app --app-dir backend --reload`.

The API is mounted at `/api`; registration is `POST /api/auth/register` and login is `POST /api/auth/login`. Both endpoints accept an encrypted body using hybrid RSA-OAEP-256 + AES-256-GCM (`algorithm`, `encryptedKey`, `iv`, `ciphertext`). Registration creates the user and returns an access token and user profile.

Tracked parts are created with `POST /api/cars/{car_id}/parts`; the server assigns each part its ID and persists both the part and its car association. `DELETE /api/cars/{car_id}/parts/{part_id}` removes a tracked part, and `DELETE /api/cars/{car_id}` removes the car and any parts no longer referenced by another car.

`owners_ids` and `parts_ids` are JSON ID arrays as requested. For larger deployments, replace the JSON ownership/parts arrays with junction tables and add Alembic migrations.
