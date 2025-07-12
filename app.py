from flask import Flask, request, jsonify
from datetime import datetime
import psycopg2

app = Flask(__name__)

# Kết nối đến PostgreSQL trên Render
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
        msnv = data.get('msnv')
        baocom = data.get('baocom')
        vitri = data.get('vitri')
        ngaygio = datetime.now()

        cursor.execute(
            "INSERT INTO ten_bang (msnv, baocom, vitri, ngaygio) VALUES (%s, %s, %s, %s)",
            (msnv, baocom, vitri, ngaygio)
        )
        conn.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# ✅ Thêm route để huỷ báo cơm
@app.route('/huybaocom', methods=['POST'])
def huy_bao_com():
    data = request.get_json()
    try:
        msnv = data.get('msnv')
        vitri = data.get('vitri')
        today = datetime.now().date()

        cursor.execute("""
            DELETE FROM ten_bang
            WHERE msnv = %s AND vitri = %s AND DATE(ngaygio) = %s
        """, (msnv, vitri, today))

        conn.commit()
        return jsonify({"status": "huy_ok"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
