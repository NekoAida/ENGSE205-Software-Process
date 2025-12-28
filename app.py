from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'  # จำเป็นสำหรับ flash messages


# จำลองฐานข้อมูลห้องประชุม (Mock Data)
rooms = [
    {"id": 1, "name": "Meeting Room A", "capacity": 10},
    {"id": 2, "name": "Meeting Room B (VIP)", "capacity": 6},
    {"id": 3, "name": "Town Hall", "capacity": 50},
]

# เก็บรายการการจองทั้งหมด
# โครงสร้าง: {"id": 1, "room_id": 1, "booker_name": "...", "date": "2025-12-28", "start_time": "09:00", "end_time": "10:00"}
bookings = [
    {"id": 1, "room_id": 3, "booker_name": "HR Team", "date": "2025-12-28", "start_time": "09:00", "end_time": "12:00"},
]
next_booking_id = 2


def get_room_status(room_id):
    """ตรวจสอบสถานะห้องและรายการจองทั้งหมด"""
    room_bookings = [b for b in bookings if b['room_id'] == room_id]
    return room_bookings


def is_time_slot_available(room_id, date, start_time, end_time):
    """ตรวจสอบว่าช่วงเวลาว่างหรือไม่"""
    room_bookings = get_room_status(room_id)
    
    for booking in room_bookings:
        if booking['date'] == date:
            # ตรวจสอบว่าเวลาทับซ้อนกันหรือไม่
            if (start_time < booking['end_time'] and end_time > booking['start_time']):
                return False
    return True


# --- ส่วนของ Sprint 1: แสดงผล ---
@app.route('/')
def index():
    # หน้าแรกแสดงเฉพาะสถานะห้อง
    rooms_with_status = []
    for room in rooms:
        room_bookings = get_room_status(room['id'])
        room_data = room.copy()
        room_data['bookings'] = room_bookings
        room_data['booking_count'] = len(room_bookings)
        rooms_with_status.append(room_data)
    
    return render_template('index.html', rooms=rooms_with_status)


@app.route('/booking')
def booking():
    # หน้าการจอง - แสดงฟอร์มจองและจัดการ
    rooms_with_bookings = []
    for room in rooms:
        room_bookings = get_room_status(room['id'])
        room_data = room.copy()
        room_data['bookings'] = room_bookings
        rooms_with_bookings.append(room_data)
    
    return render_template('booking.html', rooms=rooms_with_bookings)


# --- ส่วนของ Sprint 2: การจองและยกเลิก ---
@app.route('/book/<int:room_id>', methods=['POST'])
def book_room(room_id):
    global next_booking_id
    
    booker_name = request.form.get('booker_name')
    date = request.form.get('date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    
    # หาชื่อห้อง
    room_name = next((r['name'] for r in rooms if r['id'] == room_id), "ห้องที่เลือก")
    
    # ตรวจสอบว่าช่วงเวลาว่างหรือไม่
    if is_time_slot_available(room_id, date, start_time, end_time):
        new_booking = {
            "id": next_booking_id,
            "room_id": room_id,
            "booker_name": booker_name,
            "date": date,
            "start_time": start_time,
            "end_time": end_time
        }
        bookings.append(new_booking)
        next_booking_id += 1
        flash(f'✅ จองห้อง {room_name} สำเร็จ! วันที่ {date} เวลา {start_time} - {end_time}', 'success')
    else:
        flash(f'❌ ไม่สามารถจองได้! ห้อง {room_name} ไม่ว่างในวันที่ {date} เวลา {start_time} - {end_time}', 'danger')
    
    return redirect(url_for('booking'))


@app.route('/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    global bookings
    
    # หาข้อมูลการจองก่อนลบ
    booking_to_cancel = next((b for b in bookings if b['id'] == booking_id), None)
    
    if booking_to_cancel:
        room_name = next((r['name'] for r in rooms if r['id'] == booking_to_cancel['room_id']), "ห้อง")
        bookings = [b for b in bookings if b['id'] != booking_id]
        flash(f'✅ ยกเลิกการจองห้อง {room_name} สำเร็จ!', 'success')
    else:
        flash('❌ ไม่พบการจองที่ต้องการยกเลิก', 'danger')
    
    return redirect(url_for('booking'))



if __name__ == '__main__':
    app.run(debug=True)
