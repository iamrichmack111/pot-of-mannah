import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
from datetime import datetime

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

DATABASE = 'food.db'

# Configure Rotating File Handler for logging
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(remote_addr)s - - [%(asctime)s] "%(method)s %(url)s HTTP/1.1" %(status)s -')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.before_request
def log_request_info():
    app.logger.info('Request received', extra={
        'remote_addr': request.remote_addr,
        'method': request.method,
        'url': request.path,
        'status': ''
    })

@app.after_request
def log_response_info(response):
    app.logger.info('Response sent', extra={
        'remote_addr': request.remote_addr,
        'method': request.method,
        'url': request.path,
        'status': response.status_code
    })
    return response

@app.route('/search', methods=['GET'])
@limiter.limit("10 per minute")
def search():
    query = request.args.get('query', '')
    app.logger.info(f"Search query received: {query}")

    conn = get_db_connection()
    sql = """
    SELECT
        Category,
        Description,
        Data_Kilocalories,
        Data_Protein,
        Data_Carbohydrate,
        Data_Household_Weights_2nd_Household_Weight,
        Data_Household_Weights_2nd_Household_Weight_Description
    FROM food_data
    WHERE Category LIKE ? OR Description LIKE ?
    """
    
    cursor = conn.execute(sql, (f'%{query}%', f'%{query}%'))
    rows = cursor.fetchall()
    conn.close()
    
    results = [dict(row) for row in rows]
    app.logger.info(f"Search results: {results}")

    return jsonify(results)

@app.route('/logs', methods=['GET'])
def get_logs():
    ip_address = request.args.get('ip')
    method = request.args.get('method')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    logs = []
    with open('app.log', 'r') as f:
        for line in f:
            if ip_address and ip_address not in line:
                continue
            if method and method not in line:
                continue
            if start_date or end_date:
                try:
                    # Extract timestamp from log line
                    timestamp_str = line.split(' - ')[0]
                    log_date = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                except ValueError:
                    continue
                if start_date and log_date < datetime.fromisoformat(start_date):
                    continue
                if end_date and log_date > datetime.fromisoformat(end_date):
                    continue
            logs.append(line.strip())

    return jsonify(logs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)