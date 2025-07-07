# The World of Failures - Flask Backend

This is a simple Flask web application for collecting anonymous user submissions and providing an admin-only page to view them.

## Features
- Collects anonymous user submissions via a form
- Stores submissions in a SQLite database
- Admin-only page to view all submissions (simple password login)

## Usage
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the app:
   ```sh
   python app.py
   ```
3. Visit `http://127.0.0.1:5000/` to use the submission form.
4. Visit `http://127.0.0.1:5000/login` to log in as admin (default password: `adminpassword`).

## Security Note
- Change the `app.secret_key` and admin password in `app.py` before deploying.
