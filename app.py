from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import json
import os

app = Flask(__name__)

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
    name = request.form.get('name')
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

if __name__ == '__main__':
    app.run(debug=True)