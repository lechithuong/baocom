from flask import Flask, request, jsonify
from datetime import datetime, time, timedelta
from pytz import timezone
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect(
    dbname="baocom_db",
    user="baocom_db_user",
    password="oxqGcxc4WLf2ugn5IVqKTvcVSI36NCzs",
    host="dpg-d1m4or95pdvs73aef520-a.singapore-postgres.render.com",
    port="5432"
)
cursor = conn.cursor()

tz = timezone('Asia/Ho_Chi_Minh')

@app.route('/baocom', methods=['POST'])
def bao_com():
    data = request.get_json()
    try:
        msnv = data.get("msnv")
        baocom = data.get("baocom").upper()
        vitri = data.get("vitri").upper()
        ngaygio = datetime.now(tz)
        gio = ngaygio.time()

        # Nếu báo cơm từ 15:30 hôm nay → 6:00 sáng hôm sau, thì tính ngày mai
        if gio >= time(15, 30) or gio < time(6, 0):
            ngay = (ngaygio + timedelta(days=1)).date()
        else:
            ngay = ngaygio.date()

        # Ràng buộc thời gian báo
        if baocom == "TRUA" and not (time(6, 0) <= gio <= time(9, 0)):
            return jsonify({"status": "error", "message": "Báo cơm trưa chỉ từ 6h-9h"}), 403
        if baocom == "TOI" and not (time(6, 0) <= gio <= time(15, 30)):
            return jsonify({"status": "error", "message": "Báo cơm tối chỉ từ 6h-15h30"}), 403

        # Xoá dữ liệu cũ cùng msnv, baocom trong ngày tính theo VN
        cursor.execute("""
            DELETE FROM ten_bang 
            WHERE msnv = %s AND baocom = %s AND DATE(ngaygio AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Ho_Chi_Minh') = %s
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
