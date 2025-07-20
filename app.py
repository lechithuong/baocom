from flask import Flask, request, jsonify, session
import psycopg2
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Cho phép các request từ frontend
app.secret_key = 'bi_mat_ne'

# Kết nối PostgreSQL
conn = psycopg2.connect(
    dbname="baocom_db",
    user="baocom_db_user",
    password="oxqGcxc4WLf2ugn5IVqKTvcVSI",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Route đăng nhập
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"status": "fail", "message": "Thiếu thông tin đăng nhập"}), 400

    cursor.execute("SELECT password FROM nguoidung WHERE username = %s", (username,))
    result = cursor.fetchone()

    if not result:
        return jsonify({"status": "fail", "message": "Không tìm thấy người dùng"}), 401

    db_password = result[0]
    if db_password != password:
        return jsonify({"status": "fail", "message": "Sai mật khẩu"}), 401

    session["username"] = username  # Lưu phiên đăng nhập
    return jsonify({"status": "success", "message": "Đăng nhập thành công"}), 200

# API báo cơm (yêu cầu đăng nhập trước)
@app.route("/baocom", methods=["POST"])
def bao_com():
    if "username" not in session:
        return jsonify({"status": "fail", "message": "Chưa đăng nhập"}), 401

    try:
        data = request.get_json()
        baocom = data.get("baocom")
        vitri = data.get("vitri")
        ngaygio = datetime.now()

        if not baocom or not vitri:
            return jsonify({"status": "fail", "message": "Thiếu dữ liệu"}), 400

        cursor.execute(
            "INSERT INTO ten_bang (baocom, vitri, ngaygio, nguoidung) VALUES (%s, %s, %s, %s)",
            (baocom, vitri, ngaygio, session["username"])
        )
        conn.commit()
        return jsonify({"status": "success", "message": "Đã báo cơm thành công!"}), 200

    except Exception as e:
        print("Lỗi:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/")
def home():
    return "API Báo Cơm Đang Chạy!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
