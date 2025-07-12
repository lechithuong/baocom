from flask import Flask, request, jsonify
from datetime import datetime, time
import psycopg2
import pytz

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

# Dùng giờ Việt Nam
vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")

@app.route('/baocom', methods=['POST'])
def bao_com():
    data = request.get_json()
    try:
        msnv = data.get("msnv")
        baocom = data.get("baocom", "").strip().upper()
        vitri = data.get("vitri", "").strip().upper().replace(" ", "_")
        ngaygio = datetime.now(vn_tz)
        ngay = ngaygio.date()
        gio = ngaygio.time()

        if not msnv or not baocom or not vitri:
            return jsonify({"status": "error", "message": "Thiếu thông tin"}), 400

        # Thời gian hợp lệ
        if baocom == "TRUA" and not (time(6, 0) <= gio <= time(9, 0)):
            return jsonify({"status": "error", "message": "Chỉ được báo cơm trưa từ 6h đến 9h"}), 403
        if baocom == "TOI" and not (time(6, 0) <= gio <= time(15, 30)):
            return jsonify({"status": "error", "message": "Chỉ được báo cơm tối từ 6h đến 15h30"}), 403

        # Xoá dữ liệu cũ
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
        baocom = data.get("baocom", "").strip().upper()
        ngaygio = datetime.now(vn_tz)
        ngay = ngaygio.date()
        gio = ngaygio.time()

        if not msnv or not baocom:
            return jsonify({"status": "error", "message": "Thiếu thông tin"}), 400

        # Thời gian huỷ hợp lệ
        if baocom == "TRUA" and not (time(6, 0) <= gio <= time(9, 0)):
            return jsonify({"status": "error", "message": "Chỉ được huỷ cơm trưa từ 6h đến 9h"}), 403
        if baocom == "TOI" and not (time(6, 0) <= gio <= time(15, 30)):
            return jsonify({"status": "error", "message": "Chỉ được huỷ cơm tối từ 6h đến 15h30"}), 403

        cursor.execute("""
            DELETE FROM ten_bang 
            WHERE msnv = %s AND baocom = %s AND DATE(ngaygio) = %s
        """, (msnv, baocom, ngay))

        conn.commit()
        return jsonify({"status": "huy ok"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
