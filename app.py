from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from database import database as db

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'  # จำเป็นสำหรับ flash messages

# เริ่มต้นฐานข้อมูล
db.init_database()
db.migrate_from_json()  # ย้ายข้อมูลจาก JSON ถ้ามี

# จำลองฐานข้อมูลห้องประชุม (Mock Data)
rooms = [
    {"id": 1, "name": "Meeting Room A", "capacity": 10},
    {"id": 2, "name": "Meeting Room B (VIP)", "capacity": 6},
    {"id": 3, "name": "Town Hall", "capacity": 50},
]


def get_room_status(room_id):
    """ตรวจสอบสถานะห้องและรายการจองทั้งหมด"""
    return db.get_bookings_by_room(room_id)


def is_time_slot_available(room_id, date, start_time, end_time):
    """ตรวจสอบว่าช่วงเวลาว่างหรือไม่"""
    # ตรวจสอบว่า start_time ต้องน้อยกว่า end_time
    if start_time >= end_time:
        return False
    
    room_bookings = get_room_status(room_id)
    
    for booking in room_bookings:
        if booking['date'] == date:
            # ตรวจสอบว่าเวลาทับซ้อนกันหรือไม่
            # เงื่อนไข: มีการทับซ้อนก็ต่อเมื่อ
            # - เวลาเริ่มต้นใหม่ < เวลาสิ้นสุดเดิม AND เวลาสิ้นสุดใหม่ > เวลาเริ่มต้นเดิม
            booking_start = booking['start_time']
            booking_end = booking['end_time']
            
            # แปลงเป็น datetime object เพื่อเปรียบเทียบให้แม่นยำ
            try:
                from datetime import datetime as dt
                # สร้าง datetime object จากวันที่และเวลา
                new_start = dt.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
                new_end = dt.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
                existing_start = dt.strptime(f"{booking['date']} {booking_start}", "%Y-%m-%d %H:%M")
                existing_end = dt.strptime(f"{booking['date']} {booking_end}", "%Y-%m-%d %H:%M")
                
                # ตรวจสอบการทับซ้อน
                if (new_start < existing_end and new_end > existing_start):
                    return False
            except ValueError:
                # ถ้าแปลงไม่ได้ ใช้การเปรียบเทียบแบบง่าย (fallback)
                if (start_time < booking_end and end_time > booking_start):
                    return False
    
    return True


# --- ส่วนของ Sprint 1: แสดงผล ---
@app.route('/')
def index():
    # หน้าแรกแสดงเฉพาะสถานะห้อง
    rooms_with_status = []
    for room in rooms:
        room_bookings = db.get_bookings_by_room(room['id'])
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
        room_bookings = db.get_bookings_by_room(room['id'])
        room_data = room.copy()
        room_data['bookings'] = room_bookings
        rooms_with_bookings.append(room_data)
    
    return render_template('booking.html', rooms=rooms_with_bookings)


# --- ส่วนของ Sprint 2: การจองและยกเลิก ---
@app.route('/book/<int:room_id>', methods=['POST'])
def book_room(room_id):
    booker_name = request.form.get('booker_name')
    date = request.form.get('date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    
    # หาชื่อห้อง
    room_name = next((r['name'] for r in rooms if r['id'] == room_id), "ห้องที่เลือก")
    
    # ตรวจสอบข้อมูลที่จำเป็น
    if not all([booker_name, date, start_time, end_time]):
        flash(f'❌ กรุณากรอกข้อมูลให้ครบถ้วน!', 'danger')
        return redirect(url_for('booking'))
    
    # ตรวจสอบว่าเวลาเริ่มต้นน้อยกว่าเวลาสิ้นสุด
    if start_time >= end_time:
        flash(f'❌ เวลาเริ่มต้นต้องน้อยกว่าเวลาสิ้นสุด!', 'danger')
        return redirect(url_for('booking'))
    
    # ตรวจสอบว่าช่วงเวลาว่างหรือไม่
    if is_time_slot_available(room_id, date, start_time, end_time):
        # สร้างการจองในฐานข้อมูล (จะบันทึกประวัติอัตโนมัติ)
        booking_id = db.create_booking(room_id, booker_name, date, start_time, end_time)
        flash(f'✅ จองห้อง {room_name} สำเร็จ! วันที่ {date} เวลา {start_time} - {end_time}', 'success')
    else:
        flash(f'❌ ไม่สามารถจองได้! ห้อง {room_name} มีการจองในช่วงเวลาที่ทับซ้อนกัน (วันที่ {date} เวลา {start_time} - {end_time})', 'danger')
    
    return redirect(url_for('booking'))


@app.route('/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    # หาข้อมูลการจองก่อนลบ
    booking_to_cancel = db.get_booking_by_id(booking_id)
    
    if booking_to_cancel:
        room_name = next((r['name'] for r in rooms if r['id'] == booking_to_cancel['room_id']), "ห้อง")
        # ลบการจองและบันทึกประวัติอัตโนมัติ
        db.cancel_booking(booking_id)
        flash(f'✅ ยกเลิกการจองห้อง {room_name} สำเร็จ!', 'success')
    else:
        flash('❌ ไม่พบการจองที่ต้องการยกเลิก', 'danger')
    
    return redirect(url_for('booking'))



@app.route('/history')
def history():
    # แสดงประวัติการจองทั้งหมด
    history_records = db.get_booking_history()
    
    # เพิ่มชื่อห้องให้กับแต่ละรายการ
    for record in history_records:
        room_name = next((r['name'] for r in rooms if r['id'] == record['room_id']), 'ไม่ทราบชื่อห้อง')
        record['room_name'] = room_name
    
    return render_template('history.html', history=history_records)



if __name__ == '__main__':
    app.run(debug=True)