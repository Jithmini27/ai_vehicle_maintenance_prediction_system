from flask import Blueprint, render_template, session, redirect, url_for, Response
from utils.db import get_db_connection
import csv
import io

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def check_admin():
    return "user_id" in session and session.get("role") == "admin"


def generate_csv_response(filename, rows):
    output = io.StringIO()

    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    else:
        output.write("No data available\n")

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@admin_bp.route("/dashboard")
def admin_dashboard():
    if not check_admin():
        return redirect(url_for("auth.login"))

    return render_template(
        "admin/admin_dashboard.html",
        full_name=session.get("full_name")
    )


@admin_bp.route("/users")
def view_users():
    if not check_admin():
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT user_id, full_name, email, phone, role, status FROM users")
        users = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template("admin/manage_users.html", users=users)


@admin_bp.route("/vehicles")
def view_vehicles():
    if not check_admin():
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT vehicle_id, user_id, plate_no, brand, model, year, fuel_type,
                   last_service_date, current_mileage
            FROM vehicles
        """)
        vehicles = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template("admin/vehicles.html", vehicles=vehicles)


@admin_bp.route("/predictions")
def view_predictions():
    if not check_admin():
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM predictions")
        predictions = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template("admin/predictions.html", predictions=predictions)


@admin_bp.route("/bookings")
def view_bookings():
    if not check_admin():
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT b.*, u.full_name, v.plate_no, v.brand, v.model
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN vehicles v ON b.vehicle_id = v.vehicle_id
            ORDER BY b.booking_date DESC
        """)
        bookings = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template("admin/bookings.html", bookings=bookings)


@admin_bp.route("/reports")
def reports():
    if not check_admin():
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vehicles")
        total_vehicles = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM service_records")
        total_services = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM predictions")
        total_predictions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM bookings")
        total_bookings = cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "admin/reports.html",
        total_users=total_users,
        total_vehicles=total_vehicles,
        total_services=total_services,
        total_predictions=total_predictions,
        total_bookings=total_bookings
    )


@admin_bp.route("/analytics")
def analytics():
    if not check_admin():
        return redirect(url_for("auth.login"))

    return render_template("admin/analytics.html")


@admin_bp.route("/export/users")
def export_users():
    if not check_admin():
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT user_id, full_name, email, phone, role, status FROM users")
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return generate_csv_response("users_backup.csv", rows)


@admin_bp.route("/export/vehicles")
def export_vehicles():
    if not check_admin():
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT vehicle_id, user_id, plate_no, brand, model, year, fuel_type,
                   last_service_date, current_mileage
            FROM vehicles
        """)
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return generate_csv_response("vehicles_backup.csv", rows)


@admin_bp.route("/export/service-records")
def export_service_records():
    if not check_admin():
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM service_records")
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return generate_csv_response("service_records_backup.csv", rows)


@admin_bp.route("/export/predictions")
def export_predictions():
    if not check_admin():
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM predictions")
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return generate_csv_response("predictions_backup.csv", rows)


@admin_bp.route("/export/bookings")
def export_bookings():
    if not check_admin():
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT b.*, u.full_name, v.plate_no, v.brand, v.model
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN vehicles v ON b.vehicle_id = v.vehicle_id
            ORDER BY b.booking_date DESC
        """)
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return generate_csv_response("bookings_backup.csv", rows)