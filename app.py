from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime
import pytz
from functools import wraps

app = Flask(__name__)

# Thiết lập múi giờ Việt Nam
tz = pytz.timezone('Asia/Ho_Chi_Minh')

# Hàm kết nối database
def get_db_connection():
    return psycopg2.connect(
        dbname="baocom_db",
        user="baocom_db_user",
        password="oxqGcxc4WLf2ugn5IVqKTvcVSI",
        host="dpg-cob8g8v109ks739ol6f0-a.singapore-postgres.render.com",
        port="5432"
    )

# Hàm kiểm tra token đơn giản (có thể nâng cấp lên JWT sau)
def validate_token(username, token):
    # Trong thực tế nên kiểm tra token trong database hoặc dùng JWT
    return True

# Decorator kiểm tra đăng nhập
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json()
        username = data.get("username")
        token = request.headers.get('Authorization')
        
        if not username or not token or not validate_token(username, token):
            return jsonify({"message": "Yêu cầu đăng nhập"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/login", methods=["POST"])
def login():
    """Đăng nhập với username/password"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Vui lòng nhập username và password"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Kiểm tra tài khoản
        cur.execute(
            "SELECT username FROM accounts WHERE username = %s AND password = %s", 
            (username, password)
        )
        account = cur.fetchone()

        if account:
            # Tạo token đơn giản (trong thực tế nên dùng JWT)
            token = f"token-{username}-{datetime.now().timestamp()}"
            return jsonify({
                "message": "Đăng nhập thành công",
                "username": username,
                "token": token
            })
        else:
            return jsonify({"message": "Sai tài khoản hoặc mật khẩu"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route("/baocom", methods=["POST"])
@login_required
def bao_com():
    """Đăng ký báo cơm"""
    data = request.get_json()
    msnv = data.get("msnv")
    
    if not msnv:
        return jsonify({"message": "Thiếu mã số nhân viên"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Kiểm tra đã báo cơm hôm nay chưa
        today = datetime.now(tz).date()
        cur.execute(
            "SELECT id FROM baocom WHERE msnv = %s AND DATE(timestamp) = %s",
            (msnv, today)
        )
        
        if cur.fetchone():
            return jsonify({"message": "Bạn đã báo cơm hôm nay rồi"}), 400

        # Thêm bản ghi báo cơm
        cur.execute(
            "INSERT INTO baocom (msnv, timestamp) VALUES (%s, %s)",
            (msnv, datetime.now(tz))
        )
        conn.commit()

        return jsonify({
            "message": "Đã báo cơm thành công",
            "time": datetime.now(tz).strftime("%H:%M:%S")
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route("/huybaocom", methods=["POST"])
@login_required
def huy_bao_com():
    """Hủy báo cơm"""
    data = request.get_json()
    msnv = data.get("msnv")
    
    if not msnv:
        return jsonify({"message": "Thiếu mã số nhân viên"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Xóa báo cơm hôm nay
        today = datetime.now(tz).date()
        cur.execute(
            "DELETE FROM baocom WHERE msnv = %s AND DATE(timestamp) = %s",
            (msnv, today)
        )
        conn.commit()

        return jsonify({
            "message": "Đã hủy báo cơm thành công",
            "deleted_count": cur.rowcount
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route("/kiemtra", methods=["POST"])
@login_required
def kiemtra_baocom():
    """Kiểm tra trạng thái báo cơm"""
    data = request.get_json()
    msnv = data.get("msnv")
    
    if not msnv:
        return jsonify({"message": "Thiếu mã số nhân viên"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        today = datetime.now(tz).date()
        cur.execute(
            "SELECT timestamp FROM baocom WHERE msnv = %s AND DATE(timestamp) = %s",
            (msnv, today)
        )
        
        record = cur.fetchone()
        if record:
            return jsonify({
                "da_bao_com": True,
                "thoi_gian": record[0].strftime("%H:%M:%S")
            })
        else:
            return jsonify({"da_bao_com": False})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)