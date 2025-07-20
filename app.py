from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Hàm kết nối PostgreSQL
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

        cursor.execute("SELECT password FROM accounts WHERE username = %s", (username,))
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
    baocom = data.get('baocom')
    vitri = data.get('vitri')
    ngaygio = data.get('ngaygio')

    if not baocom or not vitri or not ngaygio:
        return jsonify({"status": "error", "message": "Thiếu dữ liệu"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO ten_bang (baocom, vitri, ngaygio) VALUES (%s, %s, %s)",
            (baocom, vitri, ngaygio)
        )
        conn.commit()

        return jsonify({"status": "success", "message": "Đã báo cơm"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
