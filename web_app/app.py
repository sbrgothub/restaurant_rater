# web_app/app.py (FINAL CLOUD VERSION)
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, text
import os

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
# This line is crucial for Render. It reads the secret URL from the environment.
DATABASE_URL = os.environ.get('DATABASE_URL')

# A check to make sure the app doesn't crash if the URL isn't set
if not DATABASE_URL:
    raise ValueError("FATAL: DATABASE_URL environment variable is not set.")
    
# Create a SQLAlchemy engine, which manages the connection pool
engine = create_engine(DATABASE_URL)

# This route is no longer used by the QR code, but is good to keep
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/rate/<unique_id>")
def rate_page(unique_id):
    try:
        with engine.connect() as conn:
            # Check if ID is valid and NEW
            result = conn.execute(
                text("SELECT id FROM transactions WHERE unique_id = :uid AND status = 'NEW'"),
                {"uid": unique_id.upper()}
            ).fetchone()
            
            if not result:
                return render_template('error.html', message="Invalid or already used ID.")

            transaction_id = result[0]
            # Get food items for this transaction
            item_results = conn.execute(
                text("SELECT food_name FROM transaction_items WHERE transaction_id = :tid"),
                {"tid": transaction_id}
            ).fetchall()
            
            food_items = sorted(list(set([item[0] for item in item_results])))
            return render_template('rate_page.html', unique_id=unique_id.upper(), food_items=food_items)

    except Exception as e:
        print(f"Database error on rate page: {e}")
        return render_template('error.html', message="A database error occurred.")


@app.route("/submit_rating", methods=["POST"])
def submit_rating():
    unique_id = request.form.get('unique_id')
    food_ratings = {key.replace('rating_', ''): int(value) for key, value in request.form.items() if key.startswith('rating_')}
    comfort = int(request.form.get('comfort_rating'))
    service = int(request.form.get('service_rating'))
    staff = int(request.form.get('staff_rating'))

    try:
        with engine.connect() as conn:
            # Start a transaction
            with conn.begin():
                # Update food ratings
                for food, stars in food_ratings.items():
                    conn.execute(
                        text("UPDATE foods SET total_stars = total_stars + :stars, rating_count = rating_count + 1 WHERE name = :fname"),
                        {"stars": stars, "fname": food}
                    )
                # Add service ratings
                conn.execute(
                    text("INSERT INTO service_ratings (comfort_rating, service_rating, staff_rating) VALUES (:c, :s, :st)"),
                    {"c": comfort, "s": service, "st": staff}
                )
                # Mark the ID as USED
                conn.execute(
                    text("UPDATE transactions SET status = 'USED' WHERE unique_id = :uid"),
                    {"uid": unique_id}
                )
            # The transaction is automatically committed here
        return redirect(url_for('thank_you'))

    except Exception as e:
        print(f"Database error on rating submission: {e}")
        return render_template('error.html', message="A database error occurred while submitting your rating.")


@app.route("/thank_you")
def thank_you():
    return render_template('thank_you.html')

# This part is for local testing. Render will use Gunicorn to run the app.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)