from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from db import get_connection
from datetime import date, datetime, timedelta

app = Flask(__name__)
app.secret_key = "bus_reservation_secret_key_2026"


# ── Helpers ──────────────────────────────────────────────────────────────────

def fmt_time(td):
    """Convert a MySQL TIME (returned as timedelta) to '08:30 AM' string."""
    if td is None:
        return ""
    if isinstance(td, timedelta):
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        hours = hours % 24          # handle values >= 24h just in case
        dt = datetime(2000, 1, 1, hours, minutes)
        return dt.strftime("%I:%M %p")
    # already a datetime/time object
    return td.strftime("%I:%M %p")


def fix_bus_times(bus_or_list):
    """Add pre-formatted time strings to bus dict(s) so templates don't call strftime on timedelta."""
    if bus_or_list is None:
        return None
    items = bus_or_list if isinstance(bus_or_list, list) else [bus_or_list]
    for b in items:
        b["dep_fmt"] = fmt_time(b.get("departure_time"))
        b["arr_fmt"] = fmt_time(b.get("arrival_time"))
    return bus_or_list


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


def get_all_cities():
    rows = query("SELECT DISTINCT source FROM buses UNION SELECT DISTINCT destination FROM buses", fetchall=True)
    return sorted([r["source"] for r in rows])


# ── Home ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    cities = get_all_cities()
    today = date.today().isoformat()
    return render_template("index.html", cities=cities, today=today)


# ── Search ────────────────────────────────────────────────────────────────────

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

    sql = """
        SELECT * FROM buses
        WHERE LOWER(source)      = LOWER(%s)
          AND LOWER(destination) = LOWER(%s)
          AND available_seats    > 0
    """
    params = [source, destination]

    if bus_type:
        sql += " AND bus_type = %s"
        params.append(bus_type)

    order_map = {
        "price":    "price ASC",
        "duration": "duration ASC",
        "rating":   "rating DESC",
        "seats":    "available_seats DESC",
    }
    sql += f" ORDER BY {order_map.get(sort_by, 'price ASC')}"

    buses = query(sql, params, fetchall=True)
    fix_bus_times(buses)

    # Parse amenities into lists
    for b in buses:
        b["amenity_list"] = [a.strip() for a in b["amenities"].split(",") if a.strip()]

    cities    = get_all_cities()
    bus_types = ["Sleeper","Semi-Sleeper","Seater","AC Sleeper","AC Seater","Volvo AC"]

    return render_template(
        "search_results.html",
        buses=buses,
        source=source,
        destination=destination,
        travel_date=travel_date,
        bus_type=bus_type,
        sort_by=sort_by,
        cities=cities,
        bus_types=bus_types,
    )


# ── Autocomplete API ──────────────────────────────────────────────────────────

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


# ── Book ──────────────────────────────────────────────────────────────────────

@app.route("/book/<int:bus_id>", methods=["GET", "POST"])
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

    # Already booked seats for this bus on this date
    booked = query(
        "SELECT seat_number FROM reservations WHERE bus_id=%s AND travel_date=%s AND status='confirmed'",
        (bus_id, travel_date), fetchall=True
    )
    booked_seats = {r["seat_number"] for r in booked}

    if request.method == "POST":
        name         = request.form["passenger_name"].strip()
        email        = request.form["passenger_email"].strip()
        phone        = request.form["passenger_phone"].strip()
        seat_str     = request.form.get("seat_number", "")
        travel_date  = request.form.get("travel_date", travel_date)

        if not name or not email or not phone or not seat_str:
            flash("All fields including seat selection are required.", "danger")
            return render_template("book.html", bus=bus, booked_seats=booked_seats, travel_date=travel_date)

        seat_number = int(seat_str)
        if seat_number in booked_seats:
            flash("That seat was just taken. Please choose another.", "warning")
            return render_template("book.html", bus=bus, booked_seats=booked_seats, travel_date=travel_date)

        query(
            "INSERT INTO reservations (passenger_name,passenger_email,passenger_phone,bus_id,seat_number,travel_date) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (name, email, phone, bus_id, seat_number, travel_date), commit=True
        )
        query("UPDATE buses SET available_seats=available_seats-1 WHERE id=%s", (bus_id,), commit=True)

        flash(f"🎉 Booking confirmed! Seat {seat_number} on {bus['bus_number']}.", "success")
        return redirect(url_for("my_tickets", email=email))

    return render_template("book.html", bus=bus, booked_seats=booked_seats, travel_date=travel_date)


# ── My Tickets ────────────────────────────────────────────────────────────────

@app.route("/my-tickets")
def my_tickets():
    email   = request.args.get("email", "").strip()
    tickets = []
    if email:
        tickets = query(
            """SELECT r.*, b.bus_number, b.operator_name, b.source, b.destination,
                      b.departure_time, b.arrival_time, b.price, b.bus_type
               FROM reservations r JOIN buses b ON r.bus_id=b.id
               WHERE r.passenger_email=%s ORDER BY r.booking_date DESC""",
            (email,), fetchall=True
        )
    if tickets:
        fix_bus_times(tickets)
    return render_template("my_tickets.html", tickets=tickets, email=email)


# ── Update ────────────────────────────────────────────────────────────────────

@app.route("/update/<int:reservation_id>", methods=["GET", "POST"])
def update(reservation_id):
    reservation = query(
        """SELECT r.*, b.bus_number, b.operator_name, b.source, b.destination,
                  b.departure_time, b.price, b.bus_type
           FROM reservations r JOIN buses b ON r.bus_id=b.id
           WHERE r.id=%s AND r.status='confirmed'""",
        (reservation_id,), fetchone=True
    )
    if not reservation:
        flash("Reservation not found or already cancelled.", "danger")
        return redirect(url_for("index"))

    fix_bus_times(reservation)

    if request.method == "POST":
        name  = request.form["passenger_name"].strip()
        email = request.form["passenger_email"].strip()
        phone = request.form["passenger_phone"].strip()
        if not name or not email or not phone:
            flash("All fields are required.", "danger")
            return render_template("update.html", reservation=reservation)
        query(
            "UPDATE reservations SET passenger_name=%s,passenger_email=%s,passenger_phone=%s WHERE id=%s",
            (name, email, phone, reservation_id), commit=True
        )
        flash("Reservation updated successfully.", "success")
        return redirect(url_for("my_tickets", email=email))

    return render_template("update.html", reservation=reservation)


# ── Cancel ────────────────────────────────────────────────────────────────────

@app.route("/cancel/<int:reservation_id>", methods=["POST"])
def cancel(reservation_id):
    reservation = query(
        "SELECT * FROM reservations WHERE id=%s AND status='confirmed'",
        (reservation_id,), fetchone=True
    )
    if not reservation:
        flash("Reservation not found or already cancelled.", "danger")
        return redirect(url_for("index"))
    query("UPDATE reservations SET status='cancelled' WHERE id=%s", (reservation_id,), commit=True)
    query("UPDATE buses SET available_seats=available_seats+1 WHERE id=%s", (reservation["bus_id"],), commit=True)
    flash("Reservation cancelled. Refund will be processed in 5-7 business days.", "info")
    return redirect(url_for("my_tickets", email=reservation["passenger_email"]))


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
