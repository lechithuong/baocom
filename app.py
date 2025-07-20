from flask import Flask, request, jsonify
from datetime import datetime
import psycopg2
import pytz
from functools import wraps

app = Flask(__name__)

# Kết nối PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname="baocom_db",
        user="baocom_db_user",
        password="oxqGcxc4WLf2ugn5IVqKTvcVSI",
        host="dpg-cnlt8en109ks73d9uf4g-a.oregon-postgres.render.com",
        port="5432",
        sslmode="require"
    )

# Set múi giờ Việt Nam
tz = pytz.timezone('Asia/Ho_Chi_Minh')

# Biến toàn cục lưu trữ token đơn giản (dùng cho demo)
user_tokens = {}

def token_required(f):
    """Decorator đơn giản để kiểm tra token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token not in user_tokens.values():
            return jsonify({"status": "error", "message": "Yêu cầu đăng nhập"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    """Đăng nhập với username/password dạng text"""
    data = request.get_json()
    try:
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"status": "error", "message": "Vui lòng nhập đủ username và password"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Kiểm tra tài khoản (không mã hóa password)
        cursor.execute(
            "SELECT username FROM accounts WHERE username = %s AND password = %s",
            (username, password)
        )
        
        if cursor.fetchone():
            # Tạo token đơn giản (trong thực tế nên dùng JWT)
            token = f"simple-token-{username}-{datetime.now().timestamp()}"
            user_tokens[username] = token
            
            return jsonify({
                "status": "success",
                "message": "Đăng nhập thành công",
                "token": token,
                "username": username
            })
        else:
            return jsonify({"status": "error", "message": "Sai tài khoản hoặc mật khẩu"}), 401

    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi hệ thống: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/baocom', methods=['POST'])
@token_required
def bao_com():
    """Báo cơm (yêu cầu đã đăng nhập)"""
    data = request.get_json()
    try:
        msnv = data.get("msnv")
        if not msnv:
            return jsonify({"status": "error", "message": "Thiếu mã số nhân viên"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Kiểm tra đã báo cơm hôm nay chưa
        today = datetime.now(tz).date()
        cursor.execute(
            "SELECT id FROM baocom WHERE msnv = %s AND DATE(timestamp AT TIME ZONE 'Asia/Ho_Chi_Minh') = %s",
            (msnv, today)
        )
        
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Bạn đã báo cơm hôm nay rồi"}), 400

        # Thêm bản ghi báo cơm
        cursor.execute(
            "INSERT INTO baocom (msnv, timestamp) VALUES (%s, %s)",
            (msnv, datetime.now(tz))
        )
        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Đã báo cơm thành công",
            "time": datetime.now(tz).strftime("%H:%M:%S")
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/huybaocom', methods=['POST'])
@token_required
def huy_bao_com():
    """Hủy báo cơm (yêu cầu đã đăng nhập)"""
    data = request.get_json()
    try:
        msnv = data.get("msnv")
        if not msnv:
            return jsonify({"status": "error", "message": "Thiếu mã số nhân viên"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        today = datetime.now(tz).date()
        cursor.execute(
            "DELETE FROM baocom WHERE msnv = %s AND DATE(timestamp AT TIME ZONE 'Asia/Ho_Chi_Minh') = %s",
            (msnv, today)
        )
        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Đã hủy báo cơm thành công",
            "deleted_count": cursor.rowcount
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/kiemtrabaocom', methods=['POST'])
@token_required
def kiemtra_bao_com():
    """Kiểm tra trạng thái báo cơm hôm nay"""
    data = request.get_json()
    try:
        msnv = data.get("msnv")
        if not msnv:
            return jsonify({"status": "error", "message": "Thiếu mã số nhân viên"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        today = datetime.now(tz).date()
        cursor.execute(
            "SELECT timestamp FROM baocom WHERE msnv = %s AND DATE(timestamp AT TIME ZONE 'Asia/Ho_Chi_Minh') = %s",
            (msnv, today)
        )
        
        record = cursor.fetchone()
        if record:
            return jsonify({
                "status": "success",
                "da_bao_com": True,
                "thoi_gian": record[0].strftime("%H:%M:%S")
            })
        else:
            return jsonify({
                "status": "success",
                "da_bao_com": False
            })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)