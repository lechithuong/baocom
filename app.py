from flask import Flask, request, jsonify
from datetime import datetime
import psycopg2
import urllib.parse

app = Flask(__name__)

# 👉 Kết nối tới Render PostgreSQL
url = "postgresql://baocom_db_user:oxqGcxc4WLf2ugn5IVqKTvcVSI36NCzs@dpg-d1m4or95pdvs73aef520-a/baocom_db"
result = urllib.parse.urlparse(url)

conn = psycopg2.connect(
    dbname=result.path[1:],
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port
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
