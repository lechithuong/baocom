from flask import Flask, request, jsonify
from datetime import datetime
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

@app.route('/baocom', methods=['POST'])
def bao_com():
    data = request.get_json()
    try:
        msnv = data.get('msnv')
        baocom = data.get('baocom')  # "TRUA" hoặc "TOI"
        vitri = data.get('vitri')    # "VAN PHONG MS", "THEO TO ANH QUY"
        ngay = datetime.now().date() # chỉ lấy ngày

        # Xoá bản ghi cùng msnv, baocom, và ngày nếu có trước đó
        cursor.execute("""
            DELETE FROM ten_bang
            WHERE msnv = %s AND baocom = %s AND DATE(ngaygio) = %s
        """, (msnv, baocom, ngay))

        # Ghi bản ghi mới
        cursor.execute("""
            INSERT INTO ten_bang (msnv, baocom, vitri, ngaygio)
            VALUES (%s, %s, %s, %s)
        """, (msnv, baocom, vitri, datetime.now()))
        
        conn.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
