import re
from datetime import datetime
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

def get_weather_data(date, time):
    pass 

def calculate_probability(data):
    probabilities = {
        'остаться на месте': 0.0,
        'двигаться с ориентированием': 0.0,
        'двигаться без ориентирования': 0.0,
        'искать укрытие': 0.0
    }

    age = data.get('Возраст', 30)
    gender = data.get('Пол', 'Неизвестно')
    physical_condition = data.get('Физическое состояние', 'Здоров')
    psychological_condition = data.get('Психическое состояние', 'Устойчив')
    experience = data.get('Опыт нахождения в дикой природе', 'Низкий')
    location = data.get('Знание местности', 'Нет')
    weather = get_weather_data(data.get('Дата'), data.get('Время'))
    has_phone = data.get('Наличие телефона', 'Нет')
    time_of_day = data.get('Время суток', 'День')
    moral_obligations = data.get('Моральные обязательства', 'Слабые')
    external_signals = data.get('Внешние сигналы', 'Нет')

    if physical_condition in ['injury', 'health_deterioration']:
        probabilities['остаться на месте'] += 0.4
    if psychological_condition == 'unstable':
        probabilities['двигаться без ориентирования'] += 0.3
    if location == 'no' or experience == 'low':
        probabilities['двигаться без ориентирования'] += 0.3
    if weather == 'bad':
        probabilities['искать укрытие'] += 0.3
    if has_phone == 'yes':
        probabilities['остаться на месте'] += 0.5
    if time_of_day in ['evening', 'night']:
        probabilities['искать укрытие'] += 0.4
    if psychological_condition == 'stable' and moral_obligations == 'strong':
        probabilities['двигаться с ориентированием'] += 0.4
    if external_signals == 'yes':
        probabilities['двигаться с ориентированием'] += 0.3
    if moral_obligations == 'strong':
        probabilities['остаться на месте'] += 0.3

    if age < 12:
        probabilities['остаться на месте'] += 0.5
        probabilities['искать укрытие'] += 0.2
    elif 12 <= age < 18:
        probabilities['двигаться без ориентирования'] += 0.4
    elif age >= 60:
        probabilities['остаться на месте'] += 0.3
        probabilities['искать укрытие'] += 0.3

    if gender == 'female':
        probabilities['искать укрытие'] += 0.2
        probabilities['остаться на месте'] += 0.2
    elif gender == 'male':
        probabilities['двигаться с ориентированием'] += 0.2
        probabilities['двигаться без ориентирования'] += 0.2

    total_probability = sum(probabilities.values())

    for key in probabilities:
        probabilities[key] /= total_probability

    return probabilities, weather

def predict_behavior(data):
    probabilities, weather = calculate_probability(data)
    probabilities_str = "\n".join([f"{behavior}: {prob * 100:.2f}%" for behavior, prob in probabilities.items()])
    return probabilities_str, weather

def get_behavior_data(data, current_time, current_date, bad_mentality=0):
    if 6 <= current_time < 12:
        times_of_day = "morning"
    elif 12 <= current_time < 18:
        times_of_day = "day"
    elif 18 <= current_time < 24:
        times_of_day = "evening"
    else:
        times_of_day = "night"

    if 0 <= current_time < 10:
        current_time = f"0{current_time}"

    mentality = str(data.get("mental_condition")) 
    if bad_mentality == 1 and mentality == "stable": 
        mentality = "unstable"

    data_behavior = {
        "Возраст": int(data.get("age")),
        "Пол": str(data.get("gender")),
        "Физическое состояние": str(data.get("physical_condition")),
        "Психическое состояние": mentality,
        "Опыт нахождения в дикой природе": str(data.get("experience")),
        "Знание местности": str(data.get("local_knowledge")),
        "Наличие телефона": str(data.get("phone")),
        "Время суток": times_of_day,
        "Моральные обязательства": "unknown",
        "Внешние сигналы": "unknown",
        "Дата": current_date,
        "Время": f"{current_time}:00"
    }

    return data_behavior, times_of_day

def get_behavior_coefficient(behavior_data):
    behavior_coefficient = 1.0

    percentages = re.findall(r"(\d+\.\d+)%", behavior_data)

    percentages = [float(p) for p in percentages]
    max_percentage = max(percentages)

    pattern = rf"([^\d]+)\s*{max_percentage:.2f}%"
    match = re.search(pattern, behavior_data)

    result_text = match.group(1).strip()

    if result_text != "остаться на месте:":
        result_text = result_text.split('%')[1].split('\n')[1]

    if result_text == "остаться на месте:":
        behavior_coefficient = 0.0
    elif result_text == "искать укрытие:":
        behavior_coefficient = 0.2

    return behavior_coefficient, result_text.capitalize() + ' ' + str(max_percentage) + '%'

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

        behavior_context = {
            'Возраст': int(data.get('age')),
            'Пол': str(data.get('gender')),
            'Физическое состояние': str(data.get('physical_condition')),
            'Психическое состояние': str(data.get('mental_condition')),
            'Опыт нахождения в дикой природе': str(data.get('experience')),
            'Знание местности': str(data.get('local_knowledge')),
            'Наличие телефона': str(data.get('phone')),
            'Время суток': 'evening', 
            'Моральные обязательства': "unknown",
            'Внешние сигналы': "unknown",
            'Дата': data.get('date_of_finding'), 
            'Время': time_of_finding_str 
        }

        behavior, _ = predict_behavior(behavior_context)

        return jsonify({
            'status': 'success',
            'coordinates_psr': coordinates_psr,
            'coordinates_finding': coordinates_finding,
            'behavior': behavior
        })
    
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Не удалось обработать запрос'}), 500

if __name__ == '__main__':
    app.run(debug=True)