# 🎬 Movie Booking API

A **FastAPI** application for booking movie tickets with support for single and group bookings, seat layouts, cancellations, and analytics.

---

## 🌐 Live Demo

Check the deployed app on Render:

[https://moviebooking-bseb.onrender.com](https://moviebooking-bseb.onrender.com)

---

## 📄 Features

- Add, list, and manage **Movies**, **Theaters**, **Halls**, and **Shows**  
- **Single seat booking** and **cancellation**  
- **Group booking**: consecutive seats auto-find or specific seat selection  
- **Group cancellation**  
- View **available seats** for a show  
- **Seat layout visualization** (JSON + ASCII)  
- Track **user booking history**  
- **Analytics** per movie (total tickets booked, GMV)  
- Seed demo data with `/seed_demo` endpoint  

---

## 🚀 API Documentation

Interactive Swagger UI is available at:

https://moviebooking-bseb.onrender.com/docs


Use Swagger to test endpoints easily:

1. `POST /seed_demo` → Create demo movie, theater, hall, show, and seats  
2. `GET /movies/` → List all movies  
3. `POST /bookings/` → Book a single seat  
4. `POST /book_group/` → Book consecutive seats as a group  
5. `POST /book_group_seats/` → Book specific seats as a group  
6. `DELETE /bookings/{id}` → Cancel a single booking  
7. `DELETE /group_cancellations/` → Cancel multiple bookings  
8. `GET /available_seats/{show_id}` → Check available seats  
9. `GET /seat_layout/{show_id}` → View hall seat layout  
10. `GET /user_bookings/{user_id}` → Check user's booking history  
11. `GET /analytics/movie/{movie_id}` → View analytics for a movie  

---

## ⚡ Seed Demo Data

To quickly populate the system with sample data, send a **POST request** to:

https://moviebooking-bseb.onrender.com/seed_demo


This will create:

- A demo movie  
- A demo theater  
- A demo hall  
- A demo show  
- Seats in the hall  

---

## 🛠 Technology Stack

- **Backend:** Python, FastAPI  
- **Database:** SQLite (SQLAlchemy ORM)  
- **Deployment:** Render  
- **API Docs:** Swagger UI (`/docs`)  

---

## 📌 Usage

1. Clone the repo:

```bash
git clone <your-github-repo-url>
cd MovieBooking
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run locally (optional):

```bash
python -m uvicorn main:app --reload --port 8000
```
4. Access:

- Root: http://127.0.0.1:8000/
- Swagger Docs: http://127.0.0.1:8000/docs

## ✅ Notes

1. This is a backend API only. No frontend UI is included.
2. All API interactions should be done via Swagger UI or HTTP clients (Postman, curl).
3. The live Render deployment URL is the easiest way to demo your project.

## 📌 Author

Developed by Priyanshu Rawat ✨