from flask import Flask, request, jsonify, make_response
import os
# pip install ping3
from ping3 import ping
import subprocess
import socket

app = Flask(__name__)

# --- Функция для ICMP-пинга ---
def icmp_ping(host):
    try:
        # Метод 1: Используя библиотеку ping3
        # Возвращает время в секундах или None/False при ошибке
        result = ping(host, timeout=3)
        if result is not None and result is not False:
            return True, round(result * 1000, 2) # возвращаем время в мс
        else:
            return False, None
    except Exception as e:
        print(f"Error using ping3: {e}")
        # Если ping3 не работает (например, из-за отсутствия привилегий или ограничений), можно попробовать subprocess
        try:
            # Метод 2: Используя системную команду ping через subprocess
            # Убедимся, что host - это IP или домен, а не что-то вредоносное
            # Базовая проверка: разрешены только буквы, цифры, точки, тире, двоеточия (IPv6), скобки (для IPv6)
            if not socket.inet_aton(host) and not all(c.isalnum() or c in '.-:[]' for c in host):
                return False, None
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "3", str(host)], # для Linux/Mac. На Windows: ["ping", "-n", "1", "-w", "3000", str(host)]
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            if result.returncode == 0:
                # subprocess не возвращает время напрямую, но мы знаем, что пинг успешен
                return True, "N/A (subprocess)" # или можно попытаться парсить вывод, но это сложнее
            else:
                return False, None
        except subprocess.TimeoutExpired:
            print("Ping subprocess timed out")
            return False, None
        except Exception as e2:
            print(f"Error using subprocess: {e2}")
            return False, None


@app.route('/ping')
def check():
    # Изменили маршрут с '/check' на '/ping' для ясности
    target = request.args.get('target') or request.args.get('host')

    if not target:
        response = make_response(jsonify({"error": "Missing 'target' or 'host' parameter"}), 400)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    # Проверка на корректность IP/домена (базовая)
    # Позволяет IPv4, IPv6, доменные имена
    # Простая проверка: содержит только разрешённые символы
    # Более строгая проверка возможна через регулярные выражения, но усложняет код
    if not all(c.isalnum() or c in '.-:[]_' for c in target):
        response = make_response(jsonify({"error": "Invalid 'target' format"}), 400)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    alive, time_ms = icmp_ping(target)

    response_data = {
        "target": target,
        "alive": alive
    }
    if time_ms is not None:
        response_data["time_ms"] = time_ms

    response = make_response(jsonify(response_data), 200)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

# Для отладки: маршрут, который всегда отвечает
@app.route('/')
def index():
    response = make_response(jsonify({"message": "ICMP Ping Server is running"}), 200)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
