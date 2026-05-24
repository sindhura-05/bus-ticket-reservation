import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from datetime import date, datetime, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "busbook_secret_2026")

# ── Flask-Login ───────────────────────────────────────────────────────────────
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to continue."
login_manager.login_message_category = "warning"

# ── Flask-Mail ────────────────────────────────────────────────────────────────
app.config["MAIL_SERVER"]   = "smtp.gmail.com"
app.config["MAIL_PORT"]     = 587
app.config["MAIL_USE_TLS"]  = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME", "noreply@busbook.com")
mail = Mail(app)


# ── User model ────────────────────────────────────────────────────────────────
class User(UserMixin):
    def __init__(self, id, full_name, email, phone):
        self.id        = id
        self.full_name = full_name
        self.email     = email
        self.phone     = phone

@login_manager.user_loader
def load_user(user_id):
    row = query("SELECT * FROM users WHERE id = %s", (user_id,), fetchone=True)
    if row:
        return User(row["id"], row["full_name"], row["email"], row["phone"])
    return None


# ── DB helper ─────────────────────────────────────────────────────────────────
def query(sql, params=(), fetchone=False, fetchall=False, commit=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params)
    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    if commit:
        conn.commit()
        result = cursor.lastrowid
    cursor.close()
    conn.close()
    return result


# ── Time helpers ──────────────────────────────────────────────────────────────
def fmt_time(td):
    if td is None:
        return ""
    if isinstance(td, timedelta):
        total = int(td.total_seconds())
        h, rem = divmod(total, 3600)
        m = rem // 60
        return datetime(2000, 1, 1, h % 24, m).strftime("%I:%M %p")
    return td.strftime("%I:%M %p")

def fix_bus_times(items):
    if items is None:
        return None
    lst = items if isinstance(items, list) else [items]
    for b in lst:
        b["dep_fmt"] = fmt_time(b.get("departure_time"))
        b["arr_fmt"] = fmt_time(b.get("arrival_time"))
    return items

def get_all_cities():
    rows = query(
        "SELECT DISTINCT source AS c FROM buses UNION SELECT DISTINCT destination FROM buses",
        fetchall=True
    )
    return sorted([r["c"] for r in rows])


# ── Email helper ──────────────────────────────────────────────────────────────
def send_booking_email(to_email, passenger_name, bus, seat_number, travel_date, reservation_id):
    try:
        msg = Message(
            subject="🎉 Booking Confirmed — BusBook",
            recipients=[to_email]
        )
        msg.html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f4f6fb;padding:20px;">
          <div style="background:#e8192c;padding:20px;border-radius:10px 10px 0 0;text-align:center;">
            <h1 style="color:#fff;margin:0;">🚌 BusBook</h1>
            <p style="color:rgba(255,255,255,.85);margin:5px 0 0;">Your ticket is confirmed!</p>
          </div>
          <div style="background:#fff;padding:24px;border-radius:0 0 10px 10px;">
            <p style="font-size:16px;">Hi <strong>{passenger_name}</strong>,</p>
            <p>Your bus ticket has been booked successfully. Here are your details:</p>
            <table style="width:100%;border-collapse:collapse;margin:16px 0;">
              <tr style="background:#f9fafb;">
                <td style="padding:10px;border:1px solid #e5e7eb;font-weight:bold;">Booking ID</td>
                <td style="padding:10px;border:1px solid #e5e7eb;">#{reservation_id}</td>
              </tr>
              <tr>
                <td style="padding:10px;border:1px solid #e5e7eb;font-weight:bold;">Route</td>
                <td style="padding:10px;border:1px solid #e5e7eb;">{bus['source']} → {bus['destination']}</td>
              </tr>
              <tr style="background:#f9fafb;">
                <td style="padding:10px;border:1px solid #e5e7eb;font-weight:bold;">Operator</td>
                <td style="padding:10px;border:1px solid #e5e7eb;">{bus['operator_name']}</td>
              </tr>
              <tr>
                <td style="padding:10px;border:1px solid #e5e7eb;font-weight:bold;">Bus Number</td>
                <td style="padding:10px;border:1px solid #e5e7eb;">{bus['bus_number']}</td>
              </tr>
              <tr style="background:#f9fafb;">
                <td style="padding:10px;border:1px solid #e5e7eb;font-weight:bold;">Travel Date</td>
                <td style="padding:10px;border:1px solid #e5e7eb;">{travel_date}</td>
              </tr>
              <tr>
                <td style="padding:10px;border:1px solid #e5e7eb;font-weight:bold;">Departure</td>
                <td style="padding:10px;border:1px solid #e5e7eb;">{bus.get('dep_fmt','')}</td>
              </tr>
              <tr style="background:#f9fafb;">
                <td style="padding:10px;border:1px solid #e5e7eb;font-weight:bold;">Seat Number</td>
                <td style="padding:10px;border:1px solid #e5e7eb;"><strong style="color:#e8192c;">Seat {seat_number}</strong></td>
              </tr>
              <tr>
                <td style="padding:10px;border:1px solid #e5e7eb;font-weight:bold;">Amount Paid</td>
                <td style="padding:10px;border:1px solid #e5e7eb;">₹{bus['price']:.0f}</td>
              </tr>
            </table>
            <p style="color:#6b7280;font-size:13px;">Please carry a valid photo ID during travel.</p>
            <p style="color:#6b7280;font-size:13px;">For support, reply to this email.</p>
            <div style="text-align:center;margin-top:20px;">
              <p style="color:#e8192c;font-weight:bold;">Have a safe journey! 🚌</p>
            </div>
          </div>
        </div>
        """
        mail.send(msg)
    except Exception as e:
        print(f"Email send failed: {e}")  # don't crash the app if email fails


# ── Auth routes ───────────────────────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        name     = request.form["full_name"].strip()
        email    = request.form["email"].strip().lower()
        phone    = request.form["phone"].strip()
        password = request.form["password"]
        confirm  = request.form["confirm_password"]

        if not all([name, email, phone, password, confirm]):
            flash("All fields are required.", "danger")
            return render_template("register.html")
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        existing = query("SELECT id FROM users WHERE email = %s", (email,), fetchone=True)
        if existing:
            flash("An account with this email already exists. Please log in.", "warning")
            return redirect(url_for("login"))

        pw_hash = generate_password_hash(password)
        query(
            "INSERT INTO users (full_name, email, phone, password_hash) VALUES (%s,%s,%s,%s)",
            (name, email, phone, pw_hash), commit=True
        )
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        email    = request.form["email"].strip().lower()
        password = request.form["password"]
        row = query("SELECT * FROM users WHERE email = %s", (email,), fetchone=True)
        if row and check_password_hash(row["password_hash"], password):
            user = User(row["id"], row["full_name"], row["email"], row["phone"])
            login_user(user, remember=request.form.get("remember") == "on")
            next_page = request.args.get("next")
            flash(f"Welcome back, {user.full_name}!", "success")
            return redirect(next_page or url_for("index"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ── Main routes ───────────────────────────────────────────────────────────────
@app.route("/")
def index():
    cities = get_all_cities()
    today  = date.today().isoformat()
    return render_template("index.html", cities=cities, today=today)


@app.route("/search")
def search():
    source      = request.args.get("source", "").strip()
    destination = request.args.get("destination", "").strip()
    travel_date = request.args.get("travel_date", date.today().isoformat())
    bus_type    = request.args.get("bus_type", "")
    sort_by     = request.args.get("sort_by", "price")

    if not source or not destination:
        flash("Please enter both source and destination.", "warning")
        return redirect(url_for("index"))

    sql = """SELECT * FROM buses
             WHERE LOWER(source)=LOWER(%s) AND LOWER(destination)=LOWER(%s)
             AND available_seats > 0"""
    params = [source, destination]
    if bus_type:
        sql += " AND bus_type = %s"
        params.append(bus_type)
    order_map = {"price":"price ASC","duration":"duration ASC","rating":"rating DESC","seats":"available_seats DESC"}
    sql += f" ORDER BY {order_map.get(sort_by,'price ASC')}"

    buses = query(sql, params, fetchall=True)
    fix_bus_times(buses)
    for b in buses:
        b["amenity_list"] = [a.strip() for a in b["amenities"].split(",") if a.strip()]

    return render_template("search_results.html",
        buses=buses, source=source, destination=destination,
        travel_date=travel_date, bus_type=bus_type, sort_by=sort_by,
        cities=get_all_cities(),
        bus_types=["Sleeper","Semi-Sleeper","Seater","AC Sleeper","AC Seater","Volvo AC"])


@app.route("/api/cities")
def api_cities():
    q = request.args.get("q", "").strip()
    rows = query(
        "SELECT DISTINCT source AS city FROM buses WHERE LOWER(source) LIKE LOWER(%s) "
        "UNION SELECT DISTINCT destination FROM buses WHERE LOWER(destination) LIKE LOWER(%s) "
        "ORDER BY city LIMIT 10",
        (f"%{q}%", f"%{q}%"), fetchall=True
    )
    return jsonify([r["city"] for r in rows])


@app.route("/book/<int:bus_id>", methods=["GET", "POST"])
@login_required
def book(bus_id):
    travel_date = request.args.get("travel_date", date.today().isoformat())
    bus = query("SELECT * FROM buses WHERE id = %s", (bus_id,), fetchone=True)
    if not bus:
        flash("Bus not found.", "danger")
        return redirect(url_for("index"))
    if bus["available_seats"] == 0:
        flash("No seats available on this bus.", "warning")
        return redirect(url_for("index"))

    fix_bus_times(bus)
    bus["amenity_list"] = [a.strip() for a in bus["amenities"].split(",") if a.strip()]
    booked = query(
        "SELECT seat_number FROM reservations WHERE bus_id=%s AND travel_date=%s AND status='confirmed'",
        (bus_id, travel_date), fetchall=True
    )
    booked_seats = {r["seat_number"] for r in booked}

    if request.method == "POST":
        name        = request.form["passenger_name"].strip()
        email       = request.form["passenger_email"].strip()
        phone       = request.form["passenger_phone"].strip()
        seat_str    = request.form.get("seat_number", "")
        travel_date = request.form.get("travel_date", travel_date)

        if not all([name, email, phone, seat_str]):
            flash("All fields including seat selection are required.", "danger")
            return render_template("book.html", bus=bus, booked_seats=booked_seats, travel_date=travel_date)

        seat_number = int(seat_str)
        if seat_number in booked_seats:
            flash("That seat was just taken. Please choose another.", "warning")
            return render_template("book.html", bus=bus, booked_seats=booked_seats, travel_date=travel_date)

        reservation_id = query(
            "INSERT INTO reservations (passenger_name,passenger_email,passenger_phone,bus_id,seat_number,travel_date,user_id) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (name, email, phone, bus_id, seat_number, travel_date, current_user.id), commit=True
        )
        query("UPDATE buses SET available_seats=available_seats-1 WHERE id=%s", (bus_id,), commit=True)

        # Send confirmation email
        send_booking_email(email, name, bus, seat_number, travel_date, reservation_id)

        flash(f"🎉 Booking confirmed! Seat {seat_number}. A confirmation email has been sent to {email}.", "success")
        return redirect(url_for("my_tickets"))

    return render_template("book.html", bus=bus, booked_seats=booked_seats, travel_date=travel_date)


@app.route("/my-tickets")
@login_required
def my_tickets():
    tickets = query(
        """SELECT r.*, b.bus_number, b.operator_name, b.source, b.destination,
                  b.departure_time, b.arrival_time, b.price, b.bus_type
           FROM reservations r JOIN buses b ON r.bus_id=b.id
           WHERE r.user_id=%s ORDER BY r.booking_date DESC""",
        (current_user.id,), fetchall=True
    )
    if tickets:
        fix_bus_times(tickets)
    return render_template("my_tickets.html", tickets=tickets)


@app.route("/update/<int:reservation_id>", methods=["GET", "POST"])
@login_required
def update(reservation_id):
    reservation = query(
        """SELECT r.*, b.bus_number, b.operator_name, b.source, b.destination,
                  b.departure_time, b.price, b.bus_type
           FROM reservations r JOIN buses b ON r.bus_id=b.id
           WHERE r.id=%s AND r.status='confirmed' AND r.user_id=%s""",
        (reservation_id, current_user.id), fetchone=True
    )
    if not reservation:
        flash("Reservation not found or access denied.", "danger")
        return redirect(url_for("my_tickets"))

    fix_bus_times(reservation)

    if request.method == "POST":
        name  = request.form["passenger_name"].strip()
        email = request.form["passenger_email"].strip()
        phone = request.form["passenger_phone"].strip()
        if not all([name, email, phone]):
            flash("All fields are required.", "danger")
            return render_template("update.html", reservation=reservation)
        query(
            "UPDATE reservations SET passenger_name=%s,passenger_email=%s,passenger_phone=%s WHERE id=%s",
            (name, email, phone, reservation_id), commit=True
        )
        flash("Reservation updated successfully.", "success")
        return redirect(url_for("my_tickets"))

    return render_template("update.html", reservation=reservation)


@app.route("/cancel/<int:reservation_id>", methods=["POST"])
@login_required
def cancel(reservation_id):
    reservation = query(
        "SELECT * FROM reservations WHERE id=%s AND status='confirmed' AND user_id=%s",
        (reservation_id, current_user.id), fetchone=True
    )
    if not reservation:
        flash("Reservation not found or access denied.", "danger")
        return redirect(url_for("my_tickets"))
    query("UPDATE reservations SET status='cancelled' WHERE id=%s", (reservation_id,), commit=True)
    query("UPDATE buses SET available_seats=available_seats+1 WHERE id=%s", (reservation["bus_id"],), commit=True)
    flash("Reservation cancelled. Refund will be processed in 5-7 business days.", "info")
    return redirect(url_for("my_tickets"))


if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
