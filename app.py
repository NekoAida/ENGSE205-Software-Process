from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# จำลองฐานข้อมูลห้องประชุม (Mock Data)
# สถานะ: True = ว่าง, False = ไม่ว่าง
rooms = [
    {"id": 1, "name": "Meeting Room A", "capacity": 10, "is_available": True, "booked_by": ""},
    {"id": 2, "name": "Meeting Room B (VIP)", "capacity": 6, "is_available": True, "booked_by": ""},
    {"id": 3, "name": "Town Hall", "capacity": 50, "is_available": False, "booked_by": "HR Team"},
]

# --- ส่วนของ Sprint 1: แสดงผล ---
@app.route('/')
def index():
    # ส่งข้อมูลห้องทั้งหมดไปแสดงที่หน้าเว็บ
    return render_template('index.html', rooms=rooms)

# --- ส่วนของ Sprint 2: การจองและยกเลิก ---
@app.route('/book/<int:room_id>', methods=['POST'])
def book_room(room_id):
    booker_name = request.form.get('booker_name')
    for room in rooms:
        if room['id'] == room_id and room['is_available']:
            room['is_available'] = False
            room['booked_by'] = booker_name
            break
    return redirect(url_for('index'))

@app.route('/cancel/<int:room_id>', methods=['POST'])
def cancel_room(room_id):
    for room in rooms:
        if room['id'] == room_id:
            room['is_available'] = True
            room['booked_by'] = ""
            break
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)