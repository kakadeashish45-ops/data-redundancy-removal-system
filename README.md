# Data Redundancy Removal System

## Live Project
https://data-redundancy-removal-system-lb14.onrender.com/# Data Redundancy Removal System

A ready-to-use academic project based on the requirements:

- Identify/classify new data as unique, duplicate, or possible false positive.
- Validate new data against existing records.
- Prevent duplicate records from being inserted.
- Append only unique and verified data to the verified dataset.
- Keep possible false positives separately for manual review.
- Use a database UNIQUE constraint on a normalized fingerprint as a second protection layer.
- Dashboard shows total, verified, duplicate-blocked and review counts.

## Technology
- Python 3
- Flask
- SQLite
- HTML/CSS
- `difflib.SequenceMatcher` for fuzzy similarity

The project follows Flask's standard application/routing approach and uses SQLite as the local database. See the official Flask documentation for the framework setup and development server. 

## Run on Windows

1. Extract the ZIP.
2. Open Command Prompt inside the project folder.
3. Create a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Start:

```bash
python app.py
```

6. Open:

http://127.0.0.1:5000

The SQLite database `redundancy.db` is created automatically.

## Test the project

Add:
- Name: Rahul Patil
- Email: rahul@gmail.com
- Phone: 9876543210

Submit the same data again. It will be blocked as a duplicate.

Then try:
- Name: Rahul P.
- Email: rahul@gmail.com
- Same phone/address

The system may classify it as a possible duplicate/false positive and put it in the review list.

## Project workflow

New Data
   ↓
Input Validation
   ↓
Normalization
   ↓
Exact Fingerprint Check
   ↓
Fuzzy Similarity Check
   ↓
+-------------------------------+
| >= 90%     → Duplicate       | → Block
| 70–89.99%  → False Positive  | → Review
| < 70%      → Unique          | → Store as Verified
+-------------------------------+
   ↓
SQLite Database

## Important note

This is a complete academic/demo implementation. For a real cloud deployment, replace SQLite with PostgreSQL/MySQL or a managed cloud database, move the secret key to an environment variable, add authentication/authorization, and use a production WSGI server.

## Suggested project title

"Data Redundancy Removal and Validation System for Cloud Databases"
