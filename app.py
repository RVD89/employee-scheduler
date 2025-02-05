from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import json
import os
import threading
import requests
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-key-for-development')

def keep_alive():
    while True:
        try:
            requests.get('https://employee-scheduler-zmgh.onrender.com')
            print("Ping sent to keep app alive")
        except:
            pass
        time.sleep(600)  # Ping every 10 minutes

if os.environ.get('RENDER'):
    threading.Thread(target=keep_alive).start()

# Ensure data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

DATA_FILE = 'data/employee_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def index():
    employees = load_data()
    return render_template('index.html', employees=employees)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form.get('employee_name')
    employees = load_data()
    if name and name not in employees:
        employees[name] = []
        save_data(employees)
    return redirect(url_for('index'))

@app.route('/add_schedule', methods=['POST'])
def add_schedule():
    employee = request.form.get('employee')
    date = request.form.get('date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    
    employees = load_data()
    if employee in employees:
        schedule = {
            'date': date,
            'start_time': start_time,
            'end_time': end_time
        }
        employees[employee].append(schedule)
        save_data(employees)
    return redirect(url_for('index'))

@app.route('/view_schedule', methods=['POST'])
def view_schedule():
    date = request.form.get('view_date')
    employees = load_data()
    schedules = []
    
    for employee, employee_schedules in employees.items():
        for schedule in employee_schedules:
            if schedule['date'] == date:
                schedule_info = {
                    'employee': employee,
                    'start_time': schedule['start_time'],
                    'end_time': schedule['end_time']
                }
                schedules.append(schedule_info)
    
    return jsonify(schedules)

@app.route('/get_calendar_events')
def get_calendar_events():
    employees = load_data()
    events = []
    
    for employee, schedules in employees.items():
        for schedule in schedules:
            events.append({
                'title': f"{employee}: {schedule['start_time']}-{schedule['end_time']}",
                'start': f"{schedule['date']}T{schedule['start_time']}",
                'end': f"{schedule['date']}T{schedule['end_time']}",
                'employee': employee
            })
    
    return jsonify(events)


if __name__ == '__main__':
    app.run(debug=True)