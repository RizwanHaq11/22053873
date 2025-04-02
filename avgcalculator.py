from flask import Flask, jsonify, request
import requests
import time
from collections import deque
from functools import lru_cache

app = Flask(__name__)

WINDOW_SIZE = 10
API_URLS = {
    "p": "http://20.244.56.144/evaluation-service/primes",
    "f": "http://20.244.56.144/evaluation-service/fibo",
    "e": "http://20.244.56.144/evaluation-service/even",
    "r": "http://20.244.56.144/evaluation-service/rand"
}

AUTH_HEADERS = {
    'Authorization':'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzQzNjA3MTc2LCJpYXQiOjE3NDM2MDY4NzYsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6IjI2YzdhM2RkLTNhNzctNGM4Mi1hNmQ3LTZmNjQwOTcwYWQ2NSIsInN1YiI6IjIyMDUzODczQGtpaXQuYWMuaW4ifSwiZW1haWwiOiIyMjA1Mzg3M0BraWl0LmFjLmluIiwibmFtZSI6Im1vaGFtbWFkIHJpendhbnVsIGhhcSIsInJvbGxObyI6IjIyMDUzODczIiwiYWNjZXNzQ29kZSI6Im53cHdyWiIsImNsaWVudElEIjoiMjZjN2EzZGQtM2E3Ny00YzgyLWE2ZDctNmY2NDA5NzBhZDY1IiwiY2xpZW50U2VjcmV0IjoiZVpTZVZDQ0NUVGpic2hKVCJ9.tRQiZPo3QunjB4scp7kGzyueMp8y0oIo3bcC5-gn8tw'
    }

window = deque()
window_set = set()
window_sum = 0

@lru_cache(maxsize=32)
def fetch_numbers_cached(category, timestamp):
    url = API_URLS.get(category)
    if not url:
        return tuple()
    try:
        response = requests.get(url, headers=AUTH_HEADERS, timeout=0.5)
        if response.status_code == 200:
            return tuple(response.json().get("numbers", []))
    except (requests.RequestException, ValueError):
        pass
    return tuple()

def fetch_numbers(category):
    timestamp = int(time.time()) // 5
    return fetch_numbers_cached(category, timestamp)

def add_to_window(num):
    global window, window_set, window_sum

    if num in window_set:
        return

    if len(window) >= WINDOW_SIZE:
        old_num = window.popleft()
        window_set.remove(old_num)
        window_sum -= old_num

    window.append(num)
    window_set.add(num)
    window_sum += num

@app.route("/numbers/<category>", methods=["GET"])
def get_numbers(category):
    if category not in API_URLS:
        return jsonify({"error": "Invalid category"}), 400

    prev_state = list(window)

    new_numbers = fetch_numbers(category)

    for num in new_numbers:
        add_to_window(num)

    avg = round(window_sum / len(window), 2) if window else 0.0

    return jsonify({
        "windowPrevState": prev_state,
        "windowCurrState": list(window),
        "numbers": new_numbers,
        "avg": avg
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9876)
