from flask import Flask, redirect, url_for
from config import Config
from routes.auth_routes import auth_bp
from routes.owner_routes import owner_bp
from routes.technician_routes import technician_bp
from routes.admin_routes import admin_bp
from routes.prediction_routes import prediction_bp
app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(auth_bp)
app.register_blueprint(prediction_bp)
app.register_blueprint(owner_bp)
app.register_blueprint(technician_bp)
app.register_blueprint(admin_bp)


@app.route("/")
def home():
    return redirect(url_for("auth.login"))


if __name__ == "__main__":
    app.run(debug=True)