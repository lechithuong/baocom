from flask import Flask, request, jsonify
from datetime import datetime
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

TABLE_NAME = "baocom"

@app.route('/baocom', methods=['POST'])
def bao_com():
    try:
        data = request.get_json()
        msnv = data.get("msnv")
        baocom = data.get("baocom", "").strip().upper()
        vitri = data.get("vitri", "").strip().upper()

        if not msnv or not baocom or not vitri:
            return jsonify({"status": "error", "message": "Thiếu msnv, baocom hoặc vitri"}), 400

        ngaygio = datetime.now()
        ngay = ngaygio.date()

        # Kiểm tra số lần đã báo hôm nay
        cursor.execute(f"""
            SELECT COUNT(*) FROM {TABLE_NAME}
            WHERE msnv = %s AND DATE(ngaygio) = %s
        """, (msnv, ngay))
        count = cursor.fetchone()[0]

        if count >= 2:
            return jsonify({"status": "error", "message": "Bạn đã báo đủ 2 bữa hôm nay"}), 403

        # Xoá nếu đã báo cùng bữa hôm nay
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
        print("❌ LỖI BAOCOM:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/huybaocom', methods=['POST'])
def huy_bao_com():
    try:
        data = request.get_json()
        msnv = data.get("msnv")
        baocom = data.get("baocom", "").strip().upper()

        if not msnv or not baocom:
            return jsonify({"status": "error", "message": "Thiếu msnv hoặc baocom"}), 400

        ngaygio = datetime.now()
        ngay = ngaygio.date()

        # Xoá báo cơm tương ứng
        cursor.execute(f"""
            DELETE FROM {TABLE_NAME}
            WHERE msnv = %s AND baocom = %s AND DATE(ngaygio) = %s
        """, (msnv, baocom, ngay))

        conn.commit()
        return jsonify({"status": "huy ok"})

    except Exception as e:
        conn.rollback()
        print("❌ LỖI HUY:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500
