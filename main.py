from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime, timezone, timedelta
import csv
import random
import string
import secrets
from gmail import is_payment_received
from send_email import send_code_to_user

app = Flask(__name__)
app.secret_key = 'your_very_strong_secret_key_123'

# Store session timeout for payment verification
SESSION_TIMEOUT_MINUTES = 5

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        payment_time = datetime.now(timezone.utc)
        if is_payment_received(payment_time):
            # Generate secure session token and unique code
            session_token = secrets.token_hex(16)
            unique_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

            # Store everything in session
            session["verified_token"] = session_token
            session["token_expiry"] = (datetime.now() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)).timestamp()
            session["unique_code"] = unique_code

            return redirect(url_for('form', token=session_token))
        else:
            return render_template("index.html", error="❌ Payment not verified. Please try again.")
    return render_template("index.html")

@app.route("/form", methods=["GET", "POST"])
def form():
    # Extract token from URL
    token = request.args.get("token")

    # Validate token and expiry
    session_token = session.get("verified_token")
    token_expiry = session.get("token_expiry")
    if not session_token or session_token != token or datetime.now().timestamp() > token_expiry:
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        code = session.get("unique_code")

        # Save to CSV
        with open("submissions.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([name, phone, email, code])
            send_code_to_user(name, phone, email, code)

        session.clear()
        return render_template("success.html", code=code)

    return render_template("form.html", code=session.get("unique_code"))

if __name__ == "__main__":
    app.run(debug=True)
<<<<<<< HEAD

=======
>>>>>>> c2afe95 (Save local changes before rebase)
