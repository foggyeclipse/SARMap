from datetime import datetime
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('base.html')

@app.route('/radius', methods=['POST'])
def radius():
    data = request.get_json()
    try:
        coordinates_psr = data.get('coordinates_psr')
        coordinates_finding = data.get('coordinates_finding')

        date_of_loss_str = data.get('date_of_loss')
        time_of_loss_str = data.get('time_of_loss', '00:00')

        date_of_finding_str = data.get('date_of_finding')
        time_of_finding_str = data.get('time_of_finding', '00:00')

        date_time_of_loss_str = f"{date_of_loss_str} {time_of_loss_str}"
        date_time_of_finding_str = f"{date_of_finding_str} {time_of_finding_str}"
        
        date_time_of_loss = datetime.strptime(date_time_of_loss_str, '%d.%m.%Y %H:%M')
        date_time_of_finding = datetime.strptime(date_time_of_finding_str, '%d.%m.%Y %H:%M')

        hours_difference = (date_time_of_finding - date_time_of_loss).total_seconds() // 3600
    
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Не удалось обработать запрос'}), 500

if __name__ == '__main__':
    app.run(debug=True)