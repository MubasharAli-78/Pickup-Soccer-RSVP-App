# Pickup Soccer RSVP & Check-in System

A complete RSVP and check-in system for pickup soccer games. Built with **Python FastAPI** (backend) and **React** (frontend).

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **RSVP IN/OUT** | Players can vote IN or OUT with automatic timestamping |
| **22-Player Limit** | First 22 players are confirmed, extras go to waitlist |
| **Timestamp Waitlist** | Waitlist is ordered by RSVP time |
| **Payment Tracking** | Mark players as paid/unpaid |
| **Game Day Check-in** | Check-in only allowed if PAID |
| **CSV Export** | Export all data with timestamps |
| **WhatsApp Ready** | API-first design for future integration |

## 🏗️ Tech Stack

**Backend:**
- Python 3.10+
- FastAPI
- SQLAlchemy + SQLite
- Pandas (CSV export)

**Frontend:**
- React 18
- Vite
- Axios

## 🚀 Quick Start

### 1. Start Backend

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```

Backend runs at: http://localhost:8000

### 2. Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend runs at: http://localhost:5173

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/players` | Get all players (categorized) |
| `POST` | `/players/rsvp` | RSVP IN or OUT |
| `PUT` | `/players/{id}/pay` | Mark as paid |
| `PUT` | `/players/{id}/checkin` | Game day check-in |
| `GET` | `/export/csv` | Download CSV |

## 🧪 Testing the System

### Full Test Flow:

1. **Add 22 players** → All show as "Confirmed"
2. **Add 23rd player** → Goes to "Waitlist #1"
3. **Mark a player PAID** → Shows "PAID" badge
4. **Check-in PAID player** → Success ✅
5. **Check-in UNPAID player** → Rejected ❌
6. **Remove confirmed player** → Waitlist player promoted
7. **Export CSV** → Downloads file with all timestamps

## 📁 Project Structure

```
Pickup Soccer RSVP App/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── database.py          # Database config
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── services/
│   │   ├── rsvp_service.py      # RSVP logic
│   │   ├── checkin_service.py   # Check-in logic
│   │   └── export_service.py    # CSV export
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main component
│   │   ├── App.css          # Styles
│   │   ├── api.js           # API service
│   │   └── components/
│   │       ├── RSVPForm.jsx
│   │       ├── PlayerList.jsx
│   │       └── AdminPanel.jsx
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## 🔮 Future WhatsApp Integration

The API is designed for easy WhatsApp integration:

```
WhatsApp Webhook → Parse Message → Call /players/rsvp → Reply with status
```

No changes needed to business logic - just add a webhook handler that:
1. Receives WhatsApp messages
2. Parses "IN" or "OUT" commands
3. Calls the existing API
4. Sends response back to WhatsApp

## 📝 Business Rules

1. **RSVP**: Backend assigns timestamp when vote is received
2. **Confirmed vs Waitlist**: First 22 IN = confirmed, rest = waitlist
3. **Payment**: Required before check-in (no payment = no entry)
4. **Promotion**: When confirmed player goes OUT, first waitlist player is promoted
5. **Waitlist Order**: Always by timestamp (first come, first served)

---

Made for Pickup Soccer ⚽
