/**
 * app.js — Shared logic for GitHub Pages prototype
 * ระบบจองห้องประชุม (Meeting Room Booking System)
 * Data persisted in browser localStorage.
 */

// ===== Room Data (static) =====
const ROOMS = [
    { id: 1, name: "Meeting Room A",       capacity: 10 },
    { id: 2, name: "Meeting Room B (VIP)", capacity: 6  },
    { id: 3, name: "Town Hall",             capacity: 50 },
];

// ===== localStorage Keys =====
const BOOKINGS_KEY = 'mrbs_bookings';
const HISTORY_KEY  = 'mrbs_history';

// ===== Helpers =====
function loadBookings() {
    return JSON.parse(localStorage.getItem(BOOKINGS_KEY) || '[]');
}

function saveBookings(bookings) {
    localStorage.setItem(BOOKINGS_KEY, JSON.stringify(bookings));
}

function loadHistory() {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
}

function saveHistory(history) {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

function nextId(arr) {
    return arr.length === 0 ? 1 : Math.max(...arr.map(b => b.id)) + 1;
}

function todayStr() {
    return new Date().toISOString().split('T')[0];
}

function nowStr() {
    return new Date().toISOString().replace('T', ' ').substring(0, 19);
}

function getRoomName(roomId) {
    const r = ROOMS.find(r => r.id === roomId);
    return r ? r.name : 'ห้องที่เลือก';
}

// ===== Booking Logic =====

/** Returns bookings for a specific room */
function getBookingsByRoom(roomId) {
    return loadBookings().filter(b => b.room_id === roomId);
}

/** Check time overlap — returns true if slot is available */
function isSlotAvailable(roomId, date, startTime, endTime) {
    if (startTime >= endTime) return false;
    const existing = getBookingsByRoom(roomId).filter(b => b.date === date);
    for (const b of existing) {
        if (startTime < b.end_time && endTime > b.start_time) return false;
    }
    return true;
}

/** Create a new booking */
function createBooking(roomId, bookerName, bookerEmail, date, startTime, endTime) {
    const bookings = loadBookings();
    const newBooking = {
        id: nextId(bookings),
        room_id: roomId,
        booker_name: bookerName,
        booker_email: bookerEmail,
        date,
        start_time: startTime,
        end_time: endTime,
    };
    bookings.push(newBooking);
    saveBookings(bookings);

    // Record history
    const history = loadHistory();
    history.unshift({
        id: nextId(history),
        action: 'created',
        action_time: nowStr(),
        room_id: roomId,
        room_name: getRoomName(roomId),
        booker_name: bookerName,
        booker_email: bookerEmail,
        date,
        start_time: startTime,
        end_time: endTime,
        notes: 'จองสำเร็จ',
    });
    saveHistory(history);
    return newBooking;
}

/** Cancel a booking by id */
function cancelBooking(bookingId) {
    const bookings = loadBookings();
    const booking = bookings.find(b => b.id === bookingId);
    if (!booking) return null;

    const updated = bookings.filter(b => b.id !== bookingId);
    saveBookings(updated);

    // Record history
    const history = loadHistory();
    history.unshift({
        id: nextId(history),
        action: 'cancelled',
        action_time: nowStr(),
        room_id: booking.room_id,
        room_name: getRoomName(booking.room_id),
        booker_name: booking.booker_name,
        booker_email: booking.booker_email,
        date: booking.date,
        start_time: booking.start_time,
        end_time: booking.end_time,
        notes: 'ยกเลิกโดยผู้ใช้',
    });
    saveHistory(history);
    return booking;
}

// ===== Toast Notifications =====
function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast-msg toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}

// ===== Escape HTML =====
function esc(str) {
    const d = document.createElement('div');
    d.appendChild(document.createTextNode(str || ''));
    return d.innerHTML;
}
