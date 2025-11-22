# Flask Portfolio Project

## Setup Instructions

1. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # on Windows
   source .venv/bin/activate  # on macOS/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create the database:
   ```bash
   python -c "from app import db; db.create_all()"
   ```

4. (Optional) Seed sample data:
   ```bash
   set FLASK_APP=app.py
   flask seed
   ```

5. Run the Flask app:
   ```bash
   python app.py
   ```

Visit http://127.0.0.1:5000 to view the site.
