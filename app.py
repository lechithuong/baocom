from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime

app = Flask(__name__)

# Hàm kết nối cơ sở dữ liệu (sử dụng riêng cho từng request)
def get_db_connection():
    return psycopg2.connect(
        dbname="baocom_db",
        user="baocom_db_user",
        password="oxqGcxc4WLf2ugn5IVqKTvcVSI",
        host="localhost",
        port="5432"
    )

# Trang chủ
@app.route("/")
def home():
    return "API Báo Cơm đang chạy!"

# Đăng nhập
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"status": "fail", "message": "Thiếu username hoặc password"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            return jsonify({"status": "success", "message": "Đăng nhập thành công!"}), 200
        else:
            return jsonify({"status": "fail", "message": "Sai thông tin đăng nhập"}), 401

    except Exception as e:
        print("Lỗi login:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

# Báo cơm
@app.route("/baocom", methods=["POST"])
def bao_com():
    try:
        data = request.get_json()
        baocom = data.get("baocom")
        vitri = data.get("vitri")
        ngaygio = datetime.now()

        if not baocom or not vitri:
            return jsonify({"status": "fail", "message": "Thiếu dữ liệu"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO baocom_logs (baocom, vitri, ngaygio) VALUES (%s, %s, %s)",
            (baocom, vitri, ngaygio)
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "success", "message": "Đã báo cơm thành công!"}), 200

    except Exception as e:
        print("Lỗi báo cơm:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
