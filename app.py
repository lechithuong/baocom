from flask import Flask, request, jsonify
from datetime import datetime
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

# Thiết lập múi giờ Việt Nam
tz = pytz.timezone('Asia/Ho_Chi_Minh')

@app.route('/baocom', methods=['POST'])
def bao_com():
    data = request.get_json()
    try:
        msnv = data.get("msnv")
        baocom = data.get("baocom").upper().replace("TRƯA", "TRUA").replace("TỐI", "TOI")
        vitri = data.get("vitri").upper()
        ngaygio = datetime.now(tz)
        ngay = ngaygio.date()

        cursor.execute("""
            DELETE FROM ten_bang 
            WHERE msnv = %s AND baocom = %s AND DATE(ngaygio AT TIME ZONE 'Asia/Ho_Chi_Minh') = %s
        """, (msnv, baocom, ngay))

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
        baocom = data.get("baocom").upper().replace("TRƯA", "TRUA").replace("TỐI", "TOI")
        ngaygio = datetime.now(tz)
        ngay = ngaygio.date()

        cursor.execute("""
            DELETE FROM ten_bang 
            WHERE msnv = %s AND baocom = %s AND DATE(ngaygio AT TIME ZONE 'Asia/Ho_Chi_Minh') = %s
        """, (msnv, baocom, ngay))

        conn.commit()
        return jsonify({"status": "huy ok"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# ✅ NEW: Xem thông tin đã báo hôm nay
@app.route('/xemthongtin', methods=['POST'])
def xem_thong_tin():
    data = request.get_json()
    try:
        msnv = data.get("msnv")
        ngaygio = datetime.now(tz)
        ngay = ngaygio.date()

        cursor.execute("""
            SELECT baocom, vitri FROM ten_bang 
            WHERE msnv = %s AND DATE(ngaygio AT TIME ZONE 'Asia/Ho_Chi_Minh') = %s
        """, (msnv, ngay))
        rows = cursor.fetchall()

        result = {}
        for row in rows:
            result[row[0]] = row[1]

        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
