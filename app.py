from flask import Flask, request, jsonify
from datetime import datetime, time, timedelta
import psycopg2

app = Flask(__name__)

# Kết nối PostgreSQL
conn = psycopg2.connect(
    dbname="baocom_db",
    user="baocom_db_user",
    password="oxqGcxc4WLf2ugn5IVqKTvcVSI36NCzs",
    host="dpg-d1m4or95pdvs73aef520-a.singapore-postgres.render.com",
    port="5432"
)
cursor = conn.cursor()

TABLE_NAME = "baocom"  # ← sửa tên bảng tại đây nếu cần

def get_ngay_hop_le(gio_hien_tai):
    """Trả về ngày phù hợp để ghi nhận"""
    if time(4, 30) <= gio_hien_tai <= time(15, 30):
        return datetime.now().date()
    else:
        return (datetime.now() + timedelta(days=1)).date()

@app.route('/baocom', methods=['POST'])
def bao_com():
    try:
        data = request.get_json()
        msnv = data.get("msnv")
        baocom = data.get("baocom", "").strip().upper()
        vitri = data.get("vitri", "").strip().upper()

        ngaygio = datetime.now()
        gio = ngaygio.time()
        ngay = get_ngay_hop_le(gio)

        # Xóa nếu đã tồn tại dòng tương ứng hôm nay
        cursor.execute(f"""
            DELETE FROM {TABLE_NAME}
            WHERE msnv = %s AND baocom = %s AND DATE(ngaygio) = %s
        """, (msnv, baocom, ngay))

        # Thêm mới
        cursor.execute(f"""
            INSERT INTO {TABLE_NAME} (msnv, baocom, vitri, ngaygio)
            VALUES (%s, %s, %s, %s)
        """, (msnv, baocom, vitri, ngaygio))

        conn.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/huybaocom', methods=['POST'])
def huy_bao_com():
    try:
        data = request.get_json()
        msnv = data.get("msnv")
        baocom = data.get("baocom", "").strip().upper()

        ngaygio = datetime.now()
        gio = ngaygio.time()
        ngay = get_ngay_hop_le(gio)

        # Xóa báo cơm tương ứng
        cursor.execute(f"""
            DELETE FROM {TABLE_NAME}
            WHERE msnv = %s AND baocom = %s AND DATE(ngaygio) = %s
        """, (msnv, baocom, ngay))

        conn.commit()
        return jsonify({"status": "huy ok"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/thongtin', methods=['GET'])
def thong_tin():
    try:
        msnv = request.args.get("msnv")
        if not msnv:
            return jsonify({"status": "error", "message": "Thiếu msnv"}), 400

        ngaygio = datetime.now()
        gio = ngaygio.time()
        ngay = get_ngay_hop_le(gio)

        cursor.execute(f"""
            SELECT baocom, vitri, ngaygio
            FROM {TABLE_NAME}
            WHERE msnv = %s AND DATE(ngaygio) = %s
            ORDER BY baocom
        """, (msnv, ngay))

        rows = cursor.fetchall()
        result = [
            {"baocom": r[0], "vitri": r[1], "ngaygio": r[2].strftime("%H:%M:%S")}
            for r in rows
        ]

        return jsonify({"status": "ok", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
