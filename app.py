from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime

app = Flask(__name__)

# Kết nối PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname="baocom_db",
        user="baocom_db_user",
        password="oxqGcxc4WLf2ugn5IVqKTvcVSI36NCzs",
        host="dpg-d1m4or95pdvs73aef520-a.singapore-postgres.render.com",
        port="5432"
    )

# API đăng nhập
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"status": "error", "message": "Thiếu username hoặc password"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM accounts WHERE username = %s", [username])
        result = cursor.fetchone()

        if result and result[0] == password:
            return jsonify({"status": "success", "message": "Đăng nhập thành công"})
        else:
            return jsonify({"status": "error", "message": "Sai tài khoản hoặc mật khẩu"}), 401

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# API báo cơm
@app.route('/baocom', methods=['POST'])
def baocom():
    data = request.get_json()
    username = data.get('username')
    vitri = data.get('vitri')

    if not username or not vitri:
        return jsonify({"status": "error", "message": "Thiếu thông tin"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        now = datetime.now()

        cursor.execute(
            "INSERT INTO ten_bang (baocom, vitri, ngaygio) VALUES (%s, %s, %s)",
            (username, vitri, now)
        )
        conn.commit()

        return jsonify({"status": "success", "message": "Báo cơm thành công"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
