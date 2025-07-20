from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime
import pytz

app = Flask(__name__)

# Kết nối đến PostgreSQL
conn = psycopg2.connect(
    dbname="baocom_db",
    user="baocom_db_user",
    password="oxqGcxc4WLf2ugn5IVqKTvcVSI",
    host="dpg-cob8g8v109ks739ol6f0-a.singapore-postgres.render.com",
    port="5432"
)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE username = %s AND password = %s", (username, password))
    account = cur.fetchone()
    cur.close()

    if account:
        return jsonify({"message": "Đăng nhập thành công", "username": username})
    else:
        return jsonify({"message": "Sai tên đăng nhập hoặc mật khẩu"}), 401

@app.route("/baocom", methods=["POST"])
def baocom():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Xác thực tài khoản
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE username = %s AND password = %s", (username, password))
    account = cur.fetchone()

    if not account:
        cur.close()
        return jsonify({"message": "Sai tài khoản hoặc mật khẩu"}), 401

    # Lấy giờ VN
    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    now = datetime.now(tz)
    date = now.date()
    time = now.time().strftime("%H:%M:%S")

    # Kiểm tra đã báo hôm nay chưa
    cur.execute("SELECT * FROM baocom WHERE username = %s AND date = %s", (username, date))
    existing = cur.fetchone()

    if existing:
        cur.close()
        return jsonify({"message": "Đã báo cơm hôm nay rồi!"}), 400

    # Thêm báo cơm mới
    cur.execute("INSERT INTO baocom (username, date, time) VALUES (%s, %s, %s)", (username, date, time))
    conn.commit()
    cur.close()

    return jsonify({"message": "Báo cơm thành công!", "date": str(date), "time": time})

if __name__ == "__main__":
    app.run(debug=True)
