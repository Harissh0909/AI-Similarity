import os
import time
import csv
import random
import string
import secrets
from datetime import datetime, timezone, timedelta
from flask import Flask, request, session, render_template, redirect, url_for, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from werkzeug.utils import secure_filename

# Local module imports
from gmail import is_payment_received
from send_email import send_code_to_user

app = Flask(__name__)
app.secret_key = 'your_very_strong_secret_key_123'

# Directories
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SESSION_TIMEOUT_MINUTES = 5

# ---------------------------- PAYMENT PAGE ---------------------------- #
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        payment_time = datetime.now(timezone.utc)
        if is_payment_received(payment_time):
            session_token = secrets.token_hex(16)
            unique_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

            session["verified_token"] = session_token
            session["token_expiry"] = (datetime.now() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)).timestamp()
            session["unique_code"] = unique_code
            session["paid"] = True  # User paid

            return redirect(url_for('form', token=session_token))
        else:
            return render_template("index.html", error="❌ Payment not verified. Please try again.")
    return render_template("index.html")

# ---------------------------- USER FORM ---------------------------- #
@app.route("/form", methods=["GET", "POST"])
def form():
    token = request.args.get("token")
    session_token = session.get("verified_token")
    token_expiry = session.get("token_expiry")

    if not session.get("paid") or not session_token or session_token != token or datetime.now().timestamp() > token_expiry:
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        code = session.get("unique_code")

        with open("submissions.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([name, phone, email, code])

        send_code_to_user(name, phone, email, code)
        session["valid_code"] = code
        session["can_verify"] = True
        return redirect(url_for('verify_code'))

    return render_template("form.html", code=session.get("unique_code"))

# ---------------------------- VERIFY CODE PAGE ---------------------------- #
@app.route("/verify_code", methods=["GET", "POST"])
def verify_code():
    if not session.get("can_verify"):
        return redirect("/")

    if request.method == "POST":
        entered_code = request.form.get("code", "").strip().upper()
        stored_code = session.get("valid_code")

        if entered_code == stored_code:
            session["can_upload"] = True
            return redirect("/upload_page")
        else:
            return render_template("verify_code.html", error="❌ Invalid code. Try again.")

    return render_template("verify_code.html")

# ---------------------------- UPLOAD PAGE ---------------------------- #
@app.route("/upload_page")
def upload_page():
    if not session.get("can_upload"):
        return redirect("/verify_code")
    return render_template("upload_online.html")

# ---------------------------- HANDLE FILE UPLOAD ---------------------------- #
@app.route("/upload", methods=["POST"])
def upload_file():
    if not session.get("can_upload"):
        return redirect("/verify_code")

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    absolute_path = os.path.abspath(filepath)

    try:
        auto_submit(absolute_path)
        return render_template("success1.html")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------------------- SELENIUM FUNCTION ---------------------------- #
def auto_submit(filepath):
    options = Options()
    options.add_argument("--headless=new")  # 'new' headless mode is more stable
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--window-size=1920x1080")

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    # Setup Chrome options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Use a unique user data directory each time (this fixes Render conflicts)
    random_profile = f"/tmp/profile_{uuid4()}"
    options.add_argument(f"--user-data-dir={random_profile}")

    # Setup Chrome driver path
    service = Service("/usr/bin/chromedriver")  # adjust this path if needed
    driver = webdriver.Chrome(service=service, options=options)
    
    wait = WebDriverWait(driver, 10)

    try:
        driver.get("https://myturnitin.report/accounts/login/")
        time.sleep(2)
        driver.find_element(By.NAME, "email").send_keys("hellomr820@gmail.com")
        driver.find_element(By.NAME, "password").send_keys("paper@123")

        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[.//span[text()="Log In"]]')))
        login_button.click()
        time.sleep(5)

        submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Submit file")]')))
        submit_btn.click()
        time.sleep(2)

        file_input = driver.find_element(By.NAME, "submitted-file")
        file_input.send_keys(filepath)
        time.sleep(2)

        final_submit = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit" and contains(@class, "btn-primary")]')))
        final_submit.click()
        time.sleep(5)

    finally:
        driver.quit()

# ---------------------------- MAIN ---------------------------- #
if __name__ == '__main__':
    app.run(debug=True)
