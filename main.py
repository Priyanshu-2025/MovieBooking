from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import crud, schemas, models
from database import Base, engine, get_db

# Create DB tables
Base.metadata.create_all(bind=engine)

# FastAPI instance
app = FastAPI(title="Movie Booking API")

# Root endpoint with friendly HTML
@app.get("/", response_class=HTMLResponse, tags=["Root"])
def read_root():
    html_content = """
    <html>
        <head>
            <title>Movie Booking API</title>
        </head>
        <body style="font-family:Arial; text-align:center; margin-top:50px;">
            <h1>🎬 Movie Booking API is Running!</h1>
            <p>Welcome to the Movie Booking API demo.</p>
            <ul style="list-style:none; padding:0;">
                <li><a href="/docs" style="font-size:20px;">📄 API Docs (/docs)</a></li>
                <li><a href="/seed_demo" style="font-size:20px;">⚡ Seed Demo Data (/seed_demo)</a></li>
            </ul>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

# Movies
@app.post("/movies/", response_model=schemas.Movie)
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    return crud.create_movie(db, movie)

@app.get("/movies/", response_model=list[schemas.Movie])
def list_movies(db: Session = Depends(get_db)):
    return crud.list_movies(db)

# Theaters
@app.post("/theaters/", response_model=schemas.Theater)
def create_theater(theater: schemas.TheaterCreate, db: Session = Depends(get_db)):
    return crud.create_theater(db, theater)

@app.get("/theaters/", response_model=list[schemas.Theater])
def list_theaters(db: Session = Depends(get_db)):
    return crud.list_theaters(db)

# Halls (auto-seed seats)
@app.post("/halls/", response_model=schemas.Hall)
def create_hall(hall: schemas.HallCreate, db: Session = Depends(get_db)):
    # default rows=5, seats_per_row=6 (change by editing crud.create_hall call)
    return crud.create_hall(db, hall, num_rows=5, seats_per_row=6)

@app.get("/halls/", response_model=list[schemas.Hall])
def list_halls(db: Session = Depends(get_db)):
    return crud.list_halls(db)

# Shows
@app.post("/shows/", response_model=schemas.Show)
def create_show(show: schemas.ShowCreate, db: Session = Depends(get_db)):
    return crud.create_show(db, show)

@app.get("/shows/", response_model=list[schemas.Show])
def list_shows(db: Session = Depends(get_db)):
    return crud.list_shows(db)

# Seats listing by hall
@app.get("/seats/{hall_id}", response_model=list[schemas.Seat])
def list_seats(hall_id: int, db: Session = Depends(get_db)):
    return crud.list_seats_by_hall(db, hall_id)

# Users
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.get("/users/", response_model=list[schemas.User])
def list_users(db: Session = Depends(get_db)):
    return crud.list_users(db)

# Bookings (single)
@app.post("/bookings/", response_model=schemas.Booking)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    res = crud.create_booking(db, booking)
    if isinstance(res, dict) and res.get("error"):
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.get("/bookings/", response_model=list[schemas.Booking])
def list_bookings(db: Session = Depends(get_db)):
    return crud.list_bookings(db)

# Cancel single booking
@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    return crud.cancel_booking(db, booking_id)

# Group booking - consecutive seats auto-find
@app.post("/book_group/", summary="Book N consecutive seats for a show (auto-find)")
def book_group_consecutive(req: schemas.GroupBookingRequest, db: Session = Depends(get_db)):
    bookings = crud.book_consecutive_seats(db, req.show_id, req.num_seats, req.user_id)
    if bookings:
        return {"message": f"Booked {len(bookings)} seats", "bookings": [{"id": b.id, "seat_id": b.seat_id} for b in bookings]}
    # suggest alternate shows
    show = db.query(models.Show).filter(models.Show.id == req.show_id).first()
    suggestions = crud.suggest_alternate_shows_for_consecutive(db, show.movie_id, req.num_seats) if show else []
    return {"error": "Could not find consecutive seats", "suggestions": suggestions}

# Group booking by explicit seat ids (friends choose seats)
@app.post("/book_group_seats/", summary="Book specific seat ids as a group")
def book_group_seats(req: schemas.GroupSeatBookingRequest, db: Session = Depends(get_db)):
    res = crud.book_specific_seats(db, req.user_id, req.show_id, req.seat_ids)
    return {
        "success_count": len(res["success"]),
        "failed": res["failed"],
        "success_ids": [b.id for b in res["success"]]
    }

# Group cancellation (by booking ids)
@app.delete("/group_cancellations/")
def group_cancel(booking_ids: list[int], db: Session = Depends(get_db)):
    cancelled = []
    not_found = []
    for bid in booking_ids:
        b = db.query(models.Booking).filter(models.Booking.id == bid).first()
        if b:
            db.delete(b)
            db.commit()
            cancelled.append(bid)
        else:
            not_found.append(bid)
    return {"cancelled": cancelled, "not_found": not_found}

# Available seats for show
@app.get("/available_seats/{show_id}")
def available_seats(show_id: int, db: Session = Depends(get_db)):
    avail = crud.available_seats_for_show(db, show_id)
    if avail is None:
        raise HTTPException(status_code=404, detail="Show not found")
    return [{"seat_id": s.id, "seat": f"{s.row}{s.number}"} for s in avail]

# Seat layout visualization (JSON + ASCII)
@app.get("/seat_layout/{show_id}")
def seat_layout(show_id: int, db: Session = Depends(get_db)):
    res = crud.seat_layout_for_show(db, show_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Show not found")
    return res

# User booking history
@app.get("/user_bookings/{user_id}")
def user_bookings(user_id: int, db: Session = Depends(get_db)):
    res = crud.bookings_for_user(db, user_id)
    if res is None:
        raise HTTPException(status_code=404, detail="User not found")
    return res

# Analytics per movie
@app.get("/analytics/movie/{movie_id}")
def analytics_movie(movie_id: int, db: Session = Depends(get_db)):
    res = crud.movie_analytics(db, movie_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return res

# Seed demo (movie, theater, hall, show, seats)
@app.post("/seed_demo/")
def seed_demo(db: Session = Depends(get_db)):
    return crud.seed_demo(db)
