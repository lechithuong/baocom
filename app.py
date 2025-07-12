from flask import Flask, request, jsonify
from datetime import datetime, time
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

@app.route('/baocom', methods=['POST'])
def bao_com():
    data = request.get_json()
    try:
        msnv = data.get("msnv")
        baocom = data.get("baocom").upper()  # "TRƯA", "TỐI" → xử lý thành "TRUA", "TOI"
        vitri = data.get("vitri").upper()
        ngaygio = datetime.now()
        ngay = ngaygio.date()
        gio = ngaygio.time()

        # Nếu là TỐI mà giờ hiện tại < 12h thì không cho báo
        if baocom == "TOI" and gio < time(12, 0):
            return jsonify({"status": "error", "message": "Chưa đến giờ báo cơm tối"}), 403
        if baocom == "TRUA" and gio > time(15, 30):
            return jsonify({"status": "error", "message": "Đã quá giờ báo cơm trưa"}), 403

        # Xoá dữ liệu cũ cùng msnv, baocom trong ngày
        cursor.execute("""
            DELETE FROM ten_bang 
            WHERE msnv = %s AND baocom = %s AND DATE(ngaygio) = %s
        """, (msnv, baocom, ngay))

        # Ghi mới
        cursor.execute("""
            INSERT INTO ten_bang (msnv, baocom, vitri, ngaygio)
            VALUES (%s, %s, %s, %s)
        """, (msnv, baocom, vitri, ngaygio))

        conn.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/huybaocom', methods=['POST'])
def huy_bao_com():
    data = request.get_json()
    try:
        msnv = data.get("msnv")
        baocom = data.get("baocom").upper()  # Phải gửi kèm "TRUA" hoặc "TOI"
        ngaygio = datetime.now()
        ngay = ngaygio.date()
        gio = ngaygio.time()

        # Kiểm tra thời gian hợp lệ
        if baocom == "TRUA" and gio > time(9, 0):
            return jsonify({"status": "error", "message": "Đã quá giờ huỷ báo cơm trưa"}), 403
        if baocom == "TOI" and gio > time(15, 30):
            return jsonify({"status": "error", "message": "Đã quá giờ huỷ báo cơm tối"}), 403

        cursor.execute("""
            DELETE FROM ten_bang 
            WHERE msnv = %s AND baocom = %s AND DATE(ngaygio) = %s
        """, (msnv, baocom, ngay))

        conn.commit()
        return jsonify({"status": "huy ok"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
