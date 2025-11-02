# app.py
from flask import Flask, request, jsonify
from cloud_capstone.organizational_unit import create_organizational_unit
from cloud_capstone.account import create_member_account
from cloud_capstone.log_handler import log_info, log_error

def create_app():
    app = Flask(__name__)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/create-ou", methods=["POST"])
    def api_create_ou():
        payload = request.get_json() or {}
        ou_name = payload.get("ou_name")
        if not ou_name:
            return jsonify({"error": "ou_name is required"}), 400
        try:
            res = create_organizational_unit(ou_name)
            return jsonify(res), 201
        except Exception as exc:
            log_error(f"API create-ou error: {exc}")
            return jsonify({"error": str(exc)}), 500

    @app.route("/create-account", methods=["POST"])
    def api_create_account():
        payload = request.get_json() or {}
        account_name = payload.get("account_name")
        account_email = payload.get("account_email")
        ou = payload.get("ou")
        role_name = payload.get("role_name", "OrgAdminRole")

        if not (account_name and account_email and ou):
            return jsonify({"error": "account_name, account_email, and ou are required"}), 400

        try:
            res = create_member_account(account_name, account_email, ou, role_name=role_name)
            return jsonify(res), 201
        except Exception as exc:
            log_error(f"API create-account error: {exc}")
            return jsonify({"error": str(exc)}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)
