from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.db import get_db_connection
import hashlib

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]
        role = request.form["role"]

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (full_name, email, password_hash, phone, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (full_name, email, password_hash, phone, role))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM users
            WHERE email = %s AND password_hash = %s AND status = 'active'
        """, (email, password_hash))

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session["user_id"] = user["user_id"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]

            if user["role"] == "owner":
                return redirect(url_for("owner.owner_dashboard"))
            elif user["role"] == "technician":
                return redirect(url_for("technician.technician_dashboard"))
            elif user["role"] == "admin":
                return redirect(url_for("admin.admin_dashboard"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")


@auth_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT user_id, full_name, email, phone, role
        FROM users
        WHERE user_id = %s
    """, (session["user_id"],))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        new_password = request.form.get("password", "").strip()

        try:
            if new_password:
                password_hash = hashlib.sha256(new_password.encode()).hexdigest()
                cursor.execute("""
                    UPDATE users
                    SET full_name = %s, email = %s, phone = %s, password_hash = %s
                    WHERE user_id = %s
                """, (full_name, email, phone, password_hash, session["user_id"]))
            else:
                cursor.execute("""
                    UPDATE users
                    SET full_name = %s, email = %s, phone = %s
                    WHERE user_id = %s
                """, (full_name, email, phone, session["user_id"]))

            conn.commit()
            session["full_name"] = full_name
            flash("Profile updated successfully.", "success")
            return redirect(url_for("auth.profile"))

        except Exception as e:
            flash(f"Error updating profile: {str(e)}", "danger")

    cursor.close()
    conn.close()

    return render_template("profile.html", user=user)


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))