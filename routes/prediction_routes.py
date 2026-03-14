from flask import Blueprint, request, jsonify
from ai_engine.predict import predict_maintenance

prediction_bp = Blueprint("prediction", __name__, url_prefix="/api")


@prediction_bp.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        result = predict_maintenance(data)

        return jsonify({
            "success": True,
            "prediction": result["prediction"],
            "risk_score": result["risk_score"]
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500