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

def get_ngay_hop_le(gio_hien_tai):
    """Xác định ngày ghi nhận phù hợp theo giờ gửi"""
    if time(4, 30) <= gio_hien_tai <= time(15, 30):
        return datetime.now().date()
    else:
        return (datetime.now() + timedelta(days=1)).date()

@app.route('/baocom', methods=['POST'])
def bao_com():
    data = request.get_json()
    try:
        msnv = data.get("msnv")
        baocom = data.get("baocom").upper().strip()  # TRUA hoặc TOI
        vitri = data.get("vitri").upper().strip()
        ngaygio = datetime.now()
        gio = ngaygio.time()
        ngay = get_ngay_hop_le(gio)

        # Kiểm tra giờ hợp lệ cho từng loại cơm
        if baocom == "TRUA" and gio > time(15, 30):
            return jsonify({"status": "error", "message": "Đã quá giờ báo cơm trưa"}), 403
        if baocom == "TOI" and gio < time(4, 30):
            return jsonify({"status": "error", "message": "Chưa đến giờ báo cơm tối"}), 403

        # Xóa báo cũ (nếu có) cho cùng ngày, cùng msnv, cùng loại cơm
        cursor.execute("""
            DELETE FROM ten_bang
            WHERE msnv = %s AND baocom = %s AND DATE(ngaygio) = %s
        """, (msnv, baocom, ngay))

        # Thêm báo cơm mới
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
        baocom = data.get("baocom").upper().strip()
        ngaygio = datetime.now()
        gio = ngaygio.time()
        ngay = get_ngay_hop_le(gio)

        # Giờ giới hạn hủy
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
