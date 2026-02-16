# ระบบจองห้องประชุม (Meeting Room Booking System)

## คำอธิบายโปรเจค
ระบบจองห้องประชุมออนไลน์ที่พัฒนาด้วย Flask สำหรับการจัดการการจองและยกเลิกการจองห้องประชุม

## สิ่งที่ต้องติดตั้ง (Prerequisites)

ก่อนรันโค้ด ให้ติดตั้ง Python และลง Library ตามนี้ใน Terminal:

```bash
pip install -r requirements.txt
```

## วิธีรัน

เปิด Terminal พิมพ์:

```bash
python app.py
```

แล้วเข้าเว็บที่ http://127.0.0.1:5000

## การตั้งค่าอีเมลแจ้งเตือน (Flask-Mail)

ระบบส่งอีเมลเมื่อจองห้องสำเร็จ โดยอ่านค่าจากไฟล์ .env (ให้สร้างเองตามตัวอย่าง .env.example)

### 1) สร้างไฟล์ .env

คัดลอกจาก .env.example แล้วกรอกค่าจริง

### 2) ค่าที่ต้องใช้

- MAIL_SERVER: โฮสต์ SMTP (เช่น Gmail = smtp.gmail.com)
- MAIL_PORT: พอร์ต SMTP (TLS ปกติคือ 587)
- MAIL_USE_TLS: ใช้ TLS หรือไม่ (true/false)
- MAIL_USERNAME: อีเมลผู้ส่ง
- MAIL_PASSWORD: รหัสผ่านสำหรับ SMTP
- MAIL_DEFAULT_SENDER: ชื่อผู้ส่งและอีเมล (รูปแบบ "Your Name <you@example.com>")

### 3) วิธีหา MAIL_PASSWORD (กรณี Gmail)

ถ้าใช้ Gmail ต้องใช้ App Password:

1. เปิด 2-Step Verification ในบัญชี Google
2. ไปที่ https://myaccount.google.com/apppasswords
3. เลือกแอปและอุปกรณ์ แล้วสร้างรหัสผ่าน
4. นำรหัสนั้นมาใส่ใน MAIL_PASSWORD

### 4) ทดสอบการส่งอีเมล

รันแอป แล้วลองจองห้อง ระบบจะส่งอีเมลยืนยันไปที่อีเมลผู้จอง

## ฟีเจอร์

- แสดงรายการห้องประชุมทั้งหมดพร้อมสถานะ
- จองห้องประชุมที่ว่าง
- ยกเลิกการจองห้องประชุม