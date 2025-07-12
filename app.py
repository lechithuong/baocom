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

def tinh_ngay_hop_le():
    now = datetime.now()
    gio = now.time()

    if time(15, 30) <= gio or gio < time(6, 0):
        if gio < time(0, 0):  # Trước nửa đêm
            return now.date() + timedelta(days=1)
        else:  # Sau nửa đêm
            return now.date()
    return now.date()

@app.route('/baocom', methods=['POST'])
def bao_com():
    data = request.get_json()
    try:
        msnv = data.get("msnv")
        baocom = data.get("baocom").upper()  # TRUA hoặc TOI
        vitri = data.get("vitri").upper()
        ngaygio = datetime.now()
        gio = ngaygio.time()
        ngay = tinh_ngay_hop_le()

        # Kiểm tra điều kiện giờ báo hợp lệ
        if baocom == "TRUA" and time(6, 0) <= gio < time(9, 0):
            pass  # ok báo cơm trưa
        elif baocom == "TOI" and time(6, 0) <= gio < time(15, 30):
            pass  # ok báo cơm tối
        elif time(15, 30) <= gio or gio < time(6, 0):
            pass  # cho phép báo trước cho ngày mai
        else:
            return jsonify({"status": "error", "message": "Ngoài giờ báo cơm"}), 403

        # Xoá cũ trước khi ghi mới
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
        baocom = data.get("baocom").upper()  # TRUA hoặc TOI
        ngaygio = datetime.now()
        gio = ngaygio.time()
        ngay = tinh_ngay_hop_le()

        # Kiểm tra thời gian huỷ hợp lệ
        if baocom == "TRUA" and time(6, 0) <= gio < time(9, 0):
            pass  # được huỷ
        elif baocom == "TOI" and time(6, 0) <= gio < time(15, 30):
            pass  # được huỷ
        elif time(15, 30) <= gio or gio < time(6, 0):
            pass  # huỷ báo cơm hôm sau
        else:
            return jsonify({"status": "error", "message": "Ngoài giờ huỷ báo cơm"}), 403

        # Xoá dòng báo cơm
        cursor.execute("""
            DELETE FROM ten_bang 
            WHERE msnv = %s AND baocom = %s AND DATE(ngaygio) = %s
        """, (msnv, baocom, ngay))

        conn.commit()
        return jsonify({"status": "huy ok"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
