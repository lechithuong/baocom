from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql

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

        # Truy vấn kiểm tra tài khoản với plain text
        cursor.execute(
            sql.SQL("SELECT password FROM accounts WHERE username = %s"),
            [username]
        )
        
        result = cursor.fetchone()
        
        if result:
            stored_password = result[0]
            if stored_password == password:
                return jsonify({"status": "success", "message": "Đăng nhập thành công"})
            else:
                return jsonify({"status": "error", "message": "Sai mật khẩu"}), 401
        else:
            return jsonify({"status": "error", "message": "Tài khoản không tồn tại"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
