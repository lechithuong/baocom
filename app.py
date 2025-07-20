from flask import Flask, request, jsonify, session
from datetime import datetime
import psycopg2
import pytz

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # cần thiết để dùng session

# Kết nối PostgreSQL
conn = psycopg2.connect(
    dbname="baocom_db",
    user="baocom_db_user",
    password="oxqGcxc4WLf2ugn5IVqKTvcVSI",
    host="localhost",  # hoặc tên host render nếu deploy
    port="5432"
)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"status": "error", "message": "Thiếu username hoặc password"}), 400

    try:
        cur = conn.cursor()
        cur.execute("SELECT password FROM accounts WHERE username = %s", (username,))
        result = cur.fetchone()
        cur.close()

        if result and result[0] == password:
            session["username"] = username
            return jsonify({"status": "success", "message": "Đăng nhập thành công"})
        else:
            return jsonify({"status": "error", "message": "Sai tài khoản hoặc mật khẩu"}), 401

    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi server: {str(e)}"}), 500

@app.route("/baocom", methods=["POST"])
def nhan_baocom():
    if "username" not in session:
        return jsonify({"status": "error", "message": "Chưa đăng nhập"}), 401

    data = request.get_json()
    msnv = data.get("msnv")
    baocom_raw = data.get("baocom")
    vitri_raw = data.get("vitri")

    if not all([msnv, baocom_raw, vitri_raw]):
        return jsonify({"status": "error", "message": "Thiếu dữ liệu"}), 400

    baocom = baocom_raw.upper().replace("TRƯA", "TRUA").replace("TỐI", "TOI")
    vitri = vitri_raw.upper()

    vietnam_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    now = datetime.now(vietnam_tz)

    try:
        cur = conn.cursor()

        # Xoá bản ghi cũ cùng ngày
        cur.execute("""
            DELETE FROM ten_bang 
            WHERE msnv = %s 
              AND baocom = %s 
              AND vitri = %s 
              AND DATE(ngaygio AT TIME ZONE 'Asia/Ho_Chi_Minh') = DATE(%s AT TIME ZONE 'Asia/Ho_Chi_Minh')
        """, (msnv, baocom, vitri, now))

        # Thêm bản ghi mới
        cur.execute("""
            INSERT INTO ten_bang (msnv, baocom, vitri, ngaygio)
            VALUES (%s, %s, %s, %s)
        """, (msnv, baocom, vitri, now))

        conn.commit()
        cur.close()
        return jsonify({"status": "success", "message": "Đã nhận báo cơm"})

    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": f"Lỗi server: {str(e)}"}), 500

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return jsonify({"status": "success", "message": "Đã đăng xuất"})

