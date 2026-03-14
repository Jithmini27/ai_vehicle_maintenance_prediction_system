
from ai_engine.predict import predict_maintenance
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from utils.db import get_db_connection
from datetime import datetime, timedelta

technician_bp = Blueprint("technician", __name__, url_prefix="/technician")


@technician_bp.route("/dashboard")
def technician_dashboard():
    if "user_id" not in session or session.get("role") != "technician":
        return redirect(url_for("auth.login"))
    return render_template("technician/technician_dashboard.html", full_name=session.get("full_name"))


@technician_bp.route("/vehicles")
def view_vehicle_details():
    if "user_id" not in session or session.get("role") != "technician":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT v.*, u.full_name
        FROM vehicles v
        JOIN users u ON v.user_id = u.user_id
        ORDER BY v.created_at DESC
    """)

    vehicles = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("technician/view_vehicle_details.html", vehicles=vehicles)


@technician_bp.route("/add-service-record/<int:vehicle_id>", methods=["GET", "POST"])
def add_service_record(vehicle_id):
    if "user_id" not in session or session.get("role") != "technician":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vehicles WHERE vehicle_id = %s", (vehicle_id,))
    vehicle = cursor.fetchone()

    if not vehicle:
        cursor.close()
        conn.close()
        flash("Vehicle not found.", "danger")
        return redirect(url_for("technician.view_vehicle_details"))

    if request.method == "POST":
        service_date = request.form["service_date"]
        odometer_reading = int(request.form["odometer_reading"])
        service_type = request.form["service_type"]
        parts_replaced = request.form["parts_replaced"]
        cost = request.form["cost"]
        notes = request.form["notes"]

        service_interval_km = int(request.form["service_interval_km"])
        next_service_suggested_km = odometer_reading + service_interval_km

        if service_interval_km <= 0:
            cursor.close()
            conn.close()
            flash("Service interval must be greater than 0.", "danger")
            return render_template("technician/add_service_record.html", vehicle=vehicle)

        maintenance_history = request.form["maintenance_history"]
        reported_issues = int(request.form["reported_issues"])
        transmission_type = request.form["transmission_type"]
        engine_size = float(request.form["engine_size"])
        owner_type = request.form["owner_type"]
        insurance_premium = float(request.form["insurance_premium"])
        service_history = int(request.form["service_history"])
        accident_history = int(request.form["accident_history"])
        fuel_efficiency = float(request.form["fuel_efficiency"])
        tire_condition = request.form["tire_condition"]
        brake_condition = request.form["brake_condition"]
        battery_status = request.form["battery_status"]

        try:
            cursor.execute("""
                INSERT INTO service_records
                (vehicle_id, service_date, odometer_reading, service_type, parts_replaced, cost, notes, next_service_suggested_km)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                vehicle_id,
                service_date,
                odometer_reading,
                service_type,
                parts_replaced,
                cost,
                notes,
                next_service_suggested_km
            ))

            cursor.execute("""
                UPDATE vehicles
                SET current_mileage = %s, last_service_date = %s
                WHERE vehicle_id = %s
            """, (odometer_reading, service_date, vehicle_id))

            vehicle_age = datetime.now().year - int(vehicle["year"]) if vehicle["year"] else 5

            sample_input = {
                "Vehicle_Model": vehicle["model"] if vehicle["model"] else "SUV",
                "Mileage": odometer_reading,
                "Maintenance_History": maintenance_history,
                "Reported_Issues": reported_issues,
                "Vehicle_Age": vehicle_age,
                "Fuel_Type": vehicle["fuel_type"] if vehicle["fuel_type"] else "Petrol",
                "Transmission_Type": transmission_type,
                "Engine_Size": engine_size,
                "Odometer_Reading": odometer_reading,
                "Last_Service_Date": str(service_date),
                "Warranty_Expiry_Date": "2026-12-31",
                "Owner_Type": owner_type,
                "Insurance_Premium": insurance_premium,
                "Service_History": service_history,
                "Accident_History": accident_history,
                "Fuel_Efficiency": fuel_efficiency,
                "Tire_Condition": tire_condition,
                "Brake_Condition": brake_condition,
                "Battery_Status": battery_status
            }

            prediction_result = predict_maintenance(sample_input)

            predicted_due_km = odometer_reading + service_interval_km
            risk_score = prediction_result["risk_score"]

            estimated_next_service_date = datetime.strptime(service_date, "%Y-%m-%d") + timedelta(days=90)
            estimated_next_service_date = estimated_next_service_date.strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT INTO predictions
                (vehicle_id, predicted_service_date, predicted_due_km, risk_score, model_version)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                vehicle_id,
                estimated_next_service_date,
                predicted_due_km,
                risk_score,
                "RandomForest_v1"
            ))

            if prediction_result["prediction"] == 1:
                notification_message = (
                    f"Maintenance alert for vehicle {vehicle['plate_no']}: "
                    f"service may be required soon. Risk Score: {risk_score}%."
                )
                notification_type = "warning"
            else:
                notification_message = (
                    f"Vehicle {vehicle['plate_no']} was analyzed. "
                    f"Current maintenance risk is low. Risk Score: {risk_score}%."
                )
                notification_type = "info"
                

            cursor.execute("""
                INSERT INTO notifications (user_id, vehicle_id, message, type)
                VALUES (%s, %s, %s, %s)
            """, (
                vehicle["user_id"],
                vehicle_id,
                notification_message,
                notification_type
            ))

            conn.commit()

            if prediction_result["prediction"] == 1:
                flash(f"Service record added. AI Alert: Maintenance required soon! Risk Score: {risk_score}%", "warning")
            else:
                flash(f"Service record added successfully. Low maintenance risk. Risk Score: {risk_score}%", "success")

            return redirect(url_for("technician.manage_service_records"))

        except Exception as e:
            flash(f"Error adding service record: {str(e)}", "danger")

    cursor.close()
    conn.close()

    return render_template("technician/add_service_record.html", vehicle=vehicle)


@technician_bp.route("/service-records")
def manage_service_records():
    if "user_id" not in session or session.get("role") != "technician":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT sr.*, v.plate_no, v.brand, v.model
        FROM service_records sr
        JOIN vehicles v ON sr.vehicle_id = v.vehicle_id
        ORDER BY sr.service_date DESC
    """)

    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("technician/manage_service_records.html", records=records)


@technician_bp.route("/bookings")
def view_bookings():
    if "user_id" not in session or session.get("role") != "technician":
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT b.*, v.plate_no, v.brand, v.model, u.full_name
        FROM bookings b
        JOIN vehicles v ON b.vehicle_id = v.vehicle_id
        JOIN users u ON b.user_id = u.user_id
        ORDER BY b.booking_date DESC
    """)

    bookings = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("technician/view_bookings.html", bookings=bookings)


@technician_bp.route("/update-booking/<int:booking_id>/<status>")
def update_booking_status(booking_id, status):
    if "user_id" not in session or session.get("role") != "technician":
        return redirect(url_for("auth.login"))

    allowed_statuses = ["pending", "confirmed", "completed", "cancelled"]
    if status not in allowed_statuses:
        flash("Invalid booking status.", "danger")
        return redirect(url_for("technician.view_bookings"))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE bookings
            SET status = %s
            WHERE booking_id = %s
        """, (status, booking_id))

        conn.commit()
        flash("Booking status updated", "success")

    except Exception as e:
        flash(str(e), "danger")

    cursor.close()
    conn.close()

    return redirect(url_for("technician.view_bookings")) 
