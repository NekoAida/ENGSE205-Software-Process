import pytest

from app import app, mail, send_email


def test_send_email_records_message():
    app.config.update(TESTING=True, MAIL_DEFAULT_SENDER='no-reply@example.com')
    with app.app_context():
        with mail.record_messages() as outbox:
            send_email(
                subject='Test Email',
                recipients=['test@example.com'],
                template='email/booking_confirmation.html',
                booking={
                    'booker_name': 'Tester',
                    'date': '2026-02-11',
                    'start_time': '10:00',
                    'end_time': '11:00',
                    'id': 42
                },
                room_name='Meeting Room A'
            )

            assert len(outbox) == 1
            msg = outbox[0]
            assert msg.subject == 'Test Email'
            # เทมเพลตภาษาไทยควรมีคำว่า ยืนยันการจอง
            assert 'ยืนยันการจอง' in msg.html
