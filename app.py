from flask import Flask, request, jsonify
from datetime import datetime
import psycopg2
import pytz

app = Flask(__name__)

# Kết nối PostgreSQL
conn = psycopg2.connect(
    dbname="baocom_db",
    user="baocom_db_user",
    password="oxqGcxc4WLf2ugn5IVqKTvcVSI",
    host="dpg-cnlt8en109ks73d9uf4g-a.oregon-postgres.render.com",
    port="5432",
    sslmode="require"
)
cursor = conn.cursor()

# Múi giờ Việt Nam
tz = pytz.timezone('Asia/Ho_Chi_Minh')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    try:
        cursor.execute(
            "SELECT 1 FROM accounts WHERE username = %s AND password = %s",
            (username, password)
        )
        if cursor.fetchone():
            return jsonify({"status": "ok", "message": "Đăng nhập thành công"})
        return jsonify({"status": "fail", "message": "Sai tài khoản hoặc mật khẩu"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/baocom', methods=['POST'])
def bao_com():
    data = request.get_json()
    msnv = data.get("msnv")
    now = datetime.now(tz)

    try:
        cursor.execute(
            "INSERT INTO baocom (msnv, timestamp) VALUES (%s, %s)",
            (msnv, now)
        )
        conn.commit()
        return jsonify({"status": "ok", "message": "Đã báo cơm thành công!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/huybaocom', methods=['POST'])
def huy_bao_com():
    data = request.get_json()
    msnv = data.get("msnv")
    today = datetime.now(tz).date()

    try:
        cursor.execute("""
            DELETE FROM baocom
            WHERE msnv = %s AND DATE(timestamp AT TIME ZONE 'Asia/Ho_Chi_Minh') = %s
        """, (msnv, today))
        conn.commit()
        return jsonify({"status": "ok", "message": "Đã huỷ báo cơm hôm nay!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
