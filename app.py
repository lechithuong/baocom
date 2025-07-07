from flask import Flask, request, jsonify
from datetime import datetime
import psycopg2
import os

app = Flask(__name__)

# Kết nối database dùng biến môi trường
conn = psycopg2.connect(
    dbname=os.environ.get("DB_NAME"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    host=os.environ.get("DB_HOST"),
    port=os.environ.get("DB_PORT", "5432")  # Mặc định là 5432 nếu không đặt
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

if __name__ == '__main__':
    app.run()
