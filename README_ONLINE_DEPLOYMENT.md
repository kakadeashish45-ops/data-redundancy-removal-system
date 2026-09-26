# Deploy online

## Easiest option: Render

1. Create a GitHub repository and upload all files in this folder.
2. Go to Render and create a new Web Service from that GitHub repository.
3. Render can use the included `render.yaml`, or enter:
   Build Command: `pip install -r requirements.txt`
   Start Command: `gunicorn app:app`
4. Deploy.
5. Render will give you a public HTTPS URL such as:
   `https://your-service-name.onrender.com`

## Important database note

This demo uses SQLite. On many cloud hosting plans, the local filesystem is not permanent across redeploys/restarts. For a real production system, use a managed PostgreSQL/MySQL database and move the connection string to an environment variable.

## Test

After deployment, open:
`https://YOUR-APP-URL/`

Health check:
`https://YOUR-APP-URL/health`
