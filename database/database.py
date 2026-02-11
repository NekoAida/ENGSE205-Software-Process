import sqlite3
from datetime import datetime
import json

DATABASE_NAME = 'room_booking.db'


def get_db_connection():
    """สร้างการเชื่อมต่อกับฐานข้อมูล"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # ให้ผลลัพธ์เป็น dict-like object
    return conn


def init_database():
    """สร้างตารางฐานข้อมูลเมื่อเริ่มต้น"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # ตารางการจองปัจจุบัน
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            booker_name TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ตารางประวัติการจองและยกเลิก
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS booking_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER,
            room_id INTEGER NOT NULL,
            booker_name TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            action TEXT NOT NULL,
            action_time TEXT DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    ''')
    
    conn.commit()
    conn.close()


def get_all_bookings():
    """ดึงรายการจองทั้งหมด"""
    conn = get_db_connection()
    bookings = conn.execute('SELECT * FROM bookings ORDER BY date, start_time').fetchall()
    conn.close()
    return [dict(booking) for booking in bookings]


def get_booking_by_id(booking_id):
    """ดึงข้อมูลการจองตาม ID"""
    conn = get_db_connection()
    booking = conn.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,)).fetchone()
    conn.close()
    return dict(booking) if booking else None


def get_bookings_by_room(room_id):
    """ดึงรายการจองของห้องใดห้องหนึ่ง"""
    conn = get_db_connection()
    bookings = conn.execute(
        'SELECT * FROM bookings WHERE room_id = ? ORDER BY date, start_time',
        (room_id,)
    ).fetchall()
    conn.close()
    return [dict(booking) for booking in bookings]


def create_booking(room_id, booker_name, date, start_time, end_time):
    """สร้างการจองใหม่"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # เพิ่มการจองใหม่
    cursor.execute('''
        INSERT INTO bookings (room_id, booker_name, date, start_time, end_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (room_id, booker_name, date, start_time, end_time))
    
    booking_id = cursor.lastrowid
    
    # บันทึกประวัติ
    cursor.execute('''
        INSERT INTO booking_history (booking_id, room_id, booker_name, date, start_time, end_time, action, notes)
        VALUES (?, ?, ?, ?, ?, ?, 'created', 'การจองถูกสร้างขึ้น')
    ''', (booking_id, room_id, booker_name, date, start_time, end_time))
    
    conn.commit()
    conn.close()
    
    return booking_id


def cancel_booking(booking_id):
    """ยกเลิกการจอง"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # ดึงข้อมูลการจองก่อนลบ
    booking = cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,)).fetchone()
    
    if booking:
        # บันทึกประวัติการยกเลิก
        cursor.execute('''
            INSERT INTO booking_history (booking_id, room_id, booker_name, date, start_time, end_time, action, notes)
            VALUES (?, ?, ?, ?, ?, ?, 'cancelled', 'การจองถูกยกเลิก')
        ''', (booking_id, booking['room_id'], booking['booker_name'], booking['date'], 
              booking['start_time'], booking['end_time']))
        
        # ลบการจอง
        cursor.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
        
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False


def get_booking_history(limit=None):
    """ดึงประวัติการจองทั้งหมด"""
    conn = get_db_connection()
    
    query = 'SELECT * FROM booking_history ORDER BY action_time DESC'
    if limit:
        query += f' LIMIT {limit}'
    
    history = conn.execute(query).fetchall()
    conn.close()
    
    return [dict(record) for record in history]


def get_booking_history_by_room(room_id, limit=None):
    """ดึงประวัติการจองของห้องใดห้องหนึ่ง"""
    conn = get_db_connection()
    
    query = 'SELECT * FROM booking_history WHERE room_id = ? ORDER BY action_time DESC'
    if limit:
        query += f' LIMIT {limit}'
    
    history = conn.execute(query, (room_id,)).fetchall()
    conn.close()
    
    return [dict(record) for record in history]


def migrate_from_json(json_file='bookings.json'):
    """ย้ายข้อมูลจาก JSON ไปยัง Database"""
    try:
        import os
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                bookings = json.load(f)
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            for booking in bookings:
                # ตรวจสอบว่ามีข้อมูลอยู่แล้วหรือไม่
                existing = cursor.execute(
                    'SELECT id FROM bookings WHERE room_id = ? AND date = ? AND start_time = ? AND end_time = ?',
                    (booking['room_id'], booking['date'], booking['start_time'], booking['end_time'])
                ).fetchone()
                
                if not existing:
                    cursor.execute('''
                        INSERT INTO bookings (room_id, booker_name, date, start_time, end_time)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (booking['room_id'], booking['booker_name'], booking['date'], 
                          booking['start_time'], booking['end_time']))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Migration completed: {len(bookings)} bookings migrated from JSON")
            return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
