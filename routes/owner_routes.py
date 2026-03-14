from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from utils.db import get_db_connection

owner_bp = Blueprint("owner", __name__, url_prefix="/owner")


@owner_bp.route("/dashboard")
def owner_dashboard():
    if "user_id" not in session or session.get("role") != "owner":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # recent notifications
    cursor.execute("""
        SELECT *
        FROM notifications
        WHERE user_id = %s AND is_read = FALSE
        ORDER BY created_at DESC
        LIMIT 5
    """, (session["user_id"],))

    recent_notifications = cursor.fetchall()

    # unread count
    cursor.execute("""
        SELECT COUNT(*) AS unread_count
        FROM notifications
        WHERE user_id = %s AND is_read = FALSE
    """, (session["user_id"],))

    result = cursor.fetchone()
    unread_count = result["unread_count"]

    cursor.close()
    conn.close()

    return render_template(
        "owner/owner_dashboard.html",
        full_name=session.get("full_name"),
        recent_notifications=recent_notifications,
        unread_count=unread_count
    )

@owner_bp.route("/add-vehicle", methods=["GET", "POST"])
def add_vehicle():
    if "user_id" not in session or session.get("role") != "owner":
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        plate_no = request.form["plate_no"]
        brand = request.form["brand"]
        model = request.form["model"]
        year = request.form["year"]
        fuel_type = request.form["fuel_type"]
        last_service_date = request.form["last_service_date"]
        current_mileage = request.form["current_mileage"]

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO vehicles
                (user_id, plate_no, brand, model, year, fuel_type, last_service_date, current_mileage)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                session["user_id"],
                plate_no,
                brand,
                model,
                year,
                fuel_type,
                last_service_date,
                current_mileage
            ))
            conn.commit()
            flash("Vehicle added successfully!", "success")
            return redirect(url_for("owner.view_vehicles"))
        except Exception as e:
            flash(f"Error adding vehicle: {str(e)}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("owner/add_vehicle.html")


@owner_bp.route("/vehicles")
def view_vehicles():
    if "user_id" not in session or session.get("role") != "owner":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM vehicles
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (session["user_id"],))

    vehicles = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("owner/view_vehicles.html", vehicles=vehicles)


@owner_bp.route("/edit-vehicle/<int:vehicle_id>", methods=["GET", "POST"])
def edit_vehicle(vehicle_id):
    if "user_id" not in session or session.get("role") != "owner":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM vehicles
        WHERE vehicle_id = %s AND user_id = %s
    """, (vehicle_id, session["user_id"]))
    vehicle = cursor.fetchone()

    if not vehicle:
        cursor.close()
        conn.close()
        flash("Vehicle not found.", "danger")
        return redirect(url_for("owner.view_vehicles"))

    if request.method == "POST":
        plate_no = request.form["plate_no"]
        brand = request.form["brand"]
        model = request.form["model"]
        year = request.form["year"]
        fuel_type = request.form["fuel_type"]
        last_service_date = request.form["last_service_date"]
        current_mileage = request.form["current_mileage"]

        try:
            cursor.execute("""
                UPDATE vehicles
                SET plate_no = %s,
                    brand = %s,
                    model = %s,
                    year = %s,
                    fuel_type = %s,
                    last_service_date = %s,
                    current_mileage = %s
                WHERE vehicle_id = %s AND user_id = %s
            """, (
                plate_no,
                brand,
                model,
                year,
                fuel_type,
                last_service_date,
                current_mileage,
                vehicle_id,
                session["user_id"]
            ))
            conn.commit()
            flash("Vehicle updated successfully!", "success")
            return redirect(url_for("owner.view_vehicles"))
        except Exception as e:
            flash(f"Error updating vehicle: {str(e)}", "danger")

    cursor.close()
    conn.close()

    return render_template("owner/edit_vehicle.html", vehicle=vehicle)


@owner_bp.route("/delete-vehicle/<int:vehicle_id>", methods=["POST"])
def delete_vehicle(vehicle_id):
    if "user_id" not in session or session.get("role") != "owner":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM vehicles
            WHERE vehicle_id = %s AND user_id = %s
        """, (vehicle_id, session["user_id"]))
        conn.commit()

        if cursor.rowcount > 0:
            flash("Vehicle deleted successfully!", "success")
        else:
            flash("Vehicle not found or could not be deleted.", "danger")

    except Exception as e:
        flash(f"Error deleting vehicle: {str(e)}", "danger")

    cursor.close()
    conn.close()

    return redirect(url_for("owner.view_vehicles"))


@owner_bp.route("/predictions")
def view_predictions():
    if "user_id" not in session or session.get("role") != "owner":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*, v.plate_no, v.brand, v.model
        FROM predictions p
        JOIN vehicles v ON p.vehicle_id = v.vehicle_id
        WHERE v.user_id = %s
        ORDER BY p.generated_at DESC
    """, (session["user_id"],))

    predictions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("owner/prediction_result.html", predictions=predictions)


@owner_bp.route("/notifications")
def view_notifications():
    if "user_id" not in session or session.get("role") != "owner":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT n.*, v.plate_no, v.brand, v.model
        FROM notifications n
        LEFT JOIN vehicles v ON n.vehicle_id = v.vehicle_id
        WHERE n.user_id = %s
        ORDER BY n.created_at DESC
    """, (session["user_id"],))

    notifications = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("owner/notifications.html", notifications=notifications)


@owner_bp.route("/mark-notification-read/<int:notification_id>", methods=["POST"])
def mark_notification_read(notification_id):
    if "user_id" not in session or session.get("role") != "owner":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE notifications
            SET is_read = TRUE
            WHERE notification_id = %s AND user_id = %s
        """, (notification_id, session["user_id"]))
        conn.commit()

        if cursor.rowcount > 0:
            flash("Notification marked as read.", "success")
        else:
            flash("Notification not found or already updated.", "danger")

    except Exception as e:
        flash(f"Error updating notification: {str(e)}", "danger")

    cursor.close()
    conn.close()

    return redirect(url_for("owner.view_notifications"))


@owner_bp.route("/mark-all-notifications-read", methods=["POST"])
def mark_all_notifications_read():
    if "user_id" not in session or session.get("role") != "owner":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE notifications
            SET is_read = TRUE
            WHERE user_id = %s AND is_read = FALSE
        """, (session["user_id"],))
        conn.commit()
        flash("All notifications marked as read.", "success")
    except Exception as e:
        flash(f"Error updating notifications: {str(e)}", "danger")

    cursor.close()
    conn.close()

    return redirect(url_for("owner.view_notifications"))


@owner_bp.route("/book-service/<int:vehicle_id>", methods=["GET", "POST"])
def book_service(vehicle_id):
    if "user_id" not in session or session.get("role") != "owner":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM vehicles
        WHERE vehicle_id = %s AND user_id = %s
    """, (vehicle_id, session["user_id"]))
    vehicle = cursor.fetchone()

    if not vehicle:
        cursor.close()
        conn.close()
        flash("Vehicle not found.", "danger")
        return redirect(url_for("owner.view_vehicles"))

    if request.method == "POST":
        booking_date = request.form["booking_date"]
        preferred_time = request.form["preferred_time"]
        remarks = request.form["remarks"]

        try:
            cursor.execute("""
                INSERT INTO bookings (user_id, vehicle_id, booking_date, preferred_time, remarks)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                session["user_id"],
                vehicle_id,
                booking_date,
                preferred_time,
                remarks
            ))
            conn.commit()
            flash("Booking submitted successfully!", "success")
            return redirect(url_for("owner.my_bookings"))
        except Exception as e:
            flash(f"Booking error: {str(e)}", "danger")

    cursor.close()
    conn.close()

    return render_template("owner/booking.html", vehicle=vehicle)


@owner_bp.route("/my-bookings")
def my_bookings():
    if "user_id" not in session or session.get("role") != "owner":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT b.*, v.plate_no, v.brand, v.model
        FROM bookings b
        JOIN vehicles v ON b.vehicle_id = v.vehicle_id
        WHERE b.user_id = %s
        ORDER BY b.booking_date DESC
    """, (session["user_id"],))

    bookings = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("owner/my_bookings.html", bookings=bookings)