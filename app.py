from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        dbname="baocom_db",
        user="baocom_db_user",
        password="oxqGcxc4WLf2ugn5IVqKTvcVSI36NCzs",
        host="dpg-d1m4or95pdvs73aef520-a.singapore-postgres.render.com",
        port="5432"
    )

# ✅ Báo cơm
@app.route('/baocom', methods=['POST'])
def baocom():
    data = request.get_json()
    msnv = data.get('msnv')
    baocom = data.get('baocom')
    vitri = data.get('vitri')

    if not msnv or not baocom or not vitri:
        return jsonify({'status': 'error', 'message': 'Thiếu dữ liệu'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        now = datetime.now()

        # 👉 Chèn vào bảng ten_bang
        cur.execute("""
            INSERT INTO ten_bang (baocom, vitri, ngaygio)
            VALUES (%s, %s, %s)
        """, (baocom, vitri, now))

        conn.commit()
        return jsonify({'status': 'success', 'message': 'Báo cơm thành công'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

    finally:
        cur.close()
        conn.close()

# ✅ Huỷ báo cơm
@app.route('/huybaocom', methods=['POST'])
def huybaocom():
    data = request.get_json()
    msnv = data.get('msnv')
    baocom = data.get('baocom')

    if not msnv or not baocom:
        return jsonify({'status': 'error', 'message': 'Thiếu dữ liệu'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 👉 Xoá báo cơm gần nhất (trong ngày) của người dùng với bữa ăn đó
        cur.execute("""
            DELETE FROM ten_bang
            WHERE baocom = %s AND ngaygio::date = CURRENT_DATE
        """, (baocom,))

        conn.commit()
        return jsonify({'status': 'success', 'message': 'Huỷ báo cơm thành công'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
