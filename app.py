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

def get_vietnam_time():
    # UTC+7 thủ công vì Render dùng UTC
    return datetime.utcnow() + timedelta(hours=7)

@app.route('/baocom', methods=['POST'])
def bao_com():
    data = request.get_json()
    try:
        msnv = data.get("msnv")
        baocom = data.get("baocom").upper()
        vitri = data.get("vitri").upper()

        ngaygio = get_vietnam_time()
        gio = ngaygio.time()

        # Tính ngày lưu
        if time(15, 30) <= gio or gio < time(6, 0):
            # Nếu từ 15h30 hôm nay đến 6h sáng → báo cho ngày mai
            ngay = (ngaygio + timedelta(days=1)).date()
        else:
            ngay = ngaygio.date()

        # Kiểm tra thời gian báo cơm hợp lệ
        if baocom == "TRUA" and not (time(6, 0) <= gio <= time(9, 0)) and not (time(15, 30) <= gio or gio < time(6, 0)):
            return jsonify({"status": "error", "message": "Đã quá giờ báo cơm trưa"}), 403
        if baocom == "TOI" and not (time(6, 0) <= gio <= time(15, 30)) and not (time(15, 30) <= gio or gio < time(6, 0)):
            return jsonify({"status": "error", "message": "Đã quá giờ báo cơm tối"}), 403

        # Xoá dữ liệu cũ cùng msnv, baocom trong ngày tính toán
        cursor.execute("""
            DELETE FROM ten_bang 
            WHERE msnv = %s AND baocom = %s AND DATE(ngaygio AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Ho_Chi_Minh') = %s
        """, (msnv, baocom, ngay))

        # Ghi dữ liệu mới
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
        baocom = data.get("baocom").upper()

        ngaygio = get_vietnam_time()
        gio = ngaygio.time()

        # Tính ngày để huỷ
        if time(15, 30) <= gio or gio < time(6, 0):
            ngay = (ngaygio + timedelta(days=1)).date()
        else:
            ngay = ngaygio.date()

        # Giới hạn huỷ
        if baocom == "TRUA" and not (time(6, 0) <= gio <= time(9, 0)):
            return jsonify({"status": "error", "message": "Đã quá giờ huỷ báo cơm trưa"}), 403
        if baocom == "TOI" and not (time(6, 0) <= gio <= time(15, 30)):
            return jsonify({"status": "error", "message": "Đã quá giờ huỷ báo cơm tối"}), 403

        cursor.execute("""
            DELETE FROM ten_bang 
            WHERE msnv = %s AND baocom = %s AND DATE(ngaygio AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Ho_Chi_Minh') = %s
        """, (msnv, baocom, ngay))

        conn.commit()
        return jsonify({"status": "huy ok"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
