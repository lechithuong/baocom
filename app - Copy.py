from flask import Flask, request, jsonify
from datetime import datetime
import psycopg2

app = Flask(__name__)

# Kết nối database (sửa lại đúng thông tin của anh)
conn = psycopg2.connect(
    dbname="Baocom",
    user="postgres",
    password="Efzezd267275",
    #host="localhost",
    host="192.168.8.10",  # không dùng localhost nữa nếu truy cập từ nơi khác
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
