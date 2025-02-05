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
        time.sleep(600)  #

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

@app.route('/schedule', methods=['POST'])
def add_schedule():
    employee = request.form.get('employee')
    date = request.form.get('date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')

    if employee and date and start_time and end_time:
        employees = load_data()
        if employee in employees:
            schedule = {
                'date': date,
                'start_time': start_time,
                'end_time': end_time
            }
            employees[employee].append(schedule)
            save_data(employees)
            return jsonify({'status': 'success'})
    
    return jsonify({'status': 'error'}), 400

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
            event = {
                'title': f"{employee}: {schedule['start_time']}-{schedule['end_time']}",
                'start': schedule['date'],
                'extendedProps': {
                    'employee': employee,
                    'start_time': schedule['start_time'],
                    'end_time': schedule['end_time']
                }
            }
            events.append(event)
    
    return jsonify(events)

@app.route('/update_schedule', methods=['POST'])
def update_schedule():
    try:
        # Get form data
        employee = request.form.get('employee')
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        old_date = request.form.get('old_date')
        old_start = request.form.get('old_start')
        old_end = request.form.get('old_end')

        print(f"Received update request:")
        print(f"Employee: {employee}")
        print(f"Old schedule: {old_date} {old_start}-{old_end}")
        print(f"New schedule: {date} {start_time}-{end_time}")

        # Load current data
        employees = load_data()
        
        if employee not in employees:
            return jsonify({'status': 'error', 'message': 'Employee not found'}), 404

        # Remove old schedule
        updated = False
        for i, schedule in enumerate(employees[employee]):
            if (schedule['date'] == old_date and 
                schedule['start_time'] == old_start and 
                schedule['end_time'] == old_end):
                employees[employee].pop(i)
                updated = True
                break
        
        if not updated:
            return jsonify({'status': 'error', 'message': 'Original schedule not found'}), 404

        # Add new schedule
        new_schedule = {
            'date': date,
            'start_time': start_time,
            'end_time': end_time
        }
        employees[employee].append(new_schedule)
        
        # Save changes
        save_data(employees)
        print("Schedule updated successfully")
        return jsonify({'status': 'success'})

    except Exception as e:
        print(f"Error in update_schedule: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)