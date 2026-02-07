# Deploy to Render

Follow these exact steps to deploy the existing repository to Render as a web service (no Docker required).

Prerequisites
- A Render account: https://render.com
- Your repo pushed to GitHub (or GitLab) and connected to your Render account

Quick overview
- Render will build the repo, install the `requirements.txt`, and run the `Procfile` command.
- Render exposes the app on an externally-routable HTTPS domain; you can map a custom domain in the Render dashboard.

Repository notes
- The app entrypoint is `Website:app` (FastAPI). The CSV used by the API is committed in the repo root: `CMU Friend Roulette Availability Responses - Form Responses 1.csv`. If that CSV is large or must be updated, consider storing it externally (S3 or a Render disk) instead of committing it.

Render settings (when creating a new Web Service)
- Environment: `Private` or `Public` (select as desired)
- Region: choose the closest region
- Branch: `main` (or whichever branch you deploy from)
- Build Command: leave blank (Render will install from `requirements.txt` automatically if using a Python environment)
- Start Command: use the Procfile (Render will run it automatically), or specify explicitly:
```
uvicorn Website:app --host 0.0.0.0 --port $PORT
```

Notes
- Render sets the `PORT` environment variable automatically. The `Procfile` added to the repository ensures the correct startup command is used.
- If you prefer a production-grade process manager, you can add `gunicorn` and use `gunicorn -k uvicorn.workers.UvicornWorker Website:app --workers 4 --bind 0.0.0.0:$PORT` as the start command. If you pick that route, add `gunicorn` to `requirements.txt`.
- If your repo contains secrets (API keys), add them under the Render Dashboard → Environment → Environment Variables rather than committing them.

Verifying the deploy
1. Push your changes to GitHub:

```zsh
git add Procfile DEPLOY_TO_RENDER.md
git commit -m "Add Procfile and Render deployment docs"
git push origin main
```

2. In Render:
  - Create a new Web Service and connect your GitHub repo.
  - Pick branch `main` and confirm the Start Command (or rely on `Procfile`).

3. After deployment finishes, open the provided Render URL and verify the site loads.

Custom domain
- In the Render dashboard, add a Custom Domain and follow the DNS instructions. Render will give you the records to add (CNAME or A) at your DNS provider. If you use Cloudflare, prefer a CNAME pointing to the Render target and set SSL to Full/Strict.

Optional improvements
- Add a `runtime.txt` (e.g., `python-3.11`) to pin Python version.
- Add `gunicorn` to `requirements.txt` for production reliability.
- Add a `render.yaml` for Infrastructure-as-Code if you want reproducible service configuration.

Need help?
- I can also add a `Dockerfile` and `render.yaml` if you prefer container-based deploys or want an IaC definition. Tell me if you want that and which Python version to pin.
