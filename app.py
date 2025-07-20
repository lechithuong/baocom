from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime

app = Flask(__name__)

# Kết nối PostgreSQL
conn = psycopg2.connect(
    dbname="baocom_db",
    user="baocom_db_user",
    password="oxqGcxc4WLf2ugn5IVqKTvcVSI",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Đăng nhập
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"status": "fail", "message": "Thiếu username hoặc password"}), 400

        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            return jsonify({"status": "success", "message": "Đăng nhập thành công!"}), 200
        else:
            return jsonify({"status": "fail", "message": "Sai thông tin đăng nhập"}), 401
    except Exception as e:
        print("Lỗi login:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

# Báo cơm (không kiểm tra đăng nhập nữa)
@app.route("/baocom", methods=["POST"])
def bao_com():
    try:
        data = request.get_json()
        baocom = data.get("baocom")
        vitri = data.get("vitri")
        ngaygio = datetime.now()

        if not baocom or not vitri:
            return jsonify({"status": "fail", "message": "Thiếu dữ liệu"}), 400

        cursor.execute(
            "INSERT INTO ten_bang (baocom, vitri, ngaygio) VALUES (%s, %s, %s)",
            (baocom, vitri, ngaygio)
        )
        conn.commit()
        return jsonify({"status": "success", "message": "Đã báo cơm thành công!"}), 200

    except Exception as e:
        print("Lỗi báo cơm:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/")
def home():
    return "API Báo Cơm đang chạy!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
