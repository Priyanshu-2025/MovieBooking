from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, func
import models, schemas

# ---------- Movies ----------
def create_movie(db: Session, movie: schemas.MovieCreate):
    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

def list_movies(db: Session):
    return db.query(models.Movie).all()

# ---------- Theaters ----------
def create_theater(db: Session, theater: schemas.TheaterCreate):
    db_theater = models.Theater(**theater.dict())
    db.add(db_theater)
    db.commit()
    db.refresh(db_theater)
    return db_theater

def list_theaters(db: Session):
    return db.query(models.Theater).all()

# ---------- Halls ----------
def create_hall(db: Session, hall: schemas.HallCreate, num_rows:int=5, seats_per_row:int=6):
    """
    Create hall and auto-seed seats (rows A.., seats 1..N).
    Default creates 5 rows x 6 seats (changeable).
    """
    db_hall = models.Hall(**{"name": hall.name, "theater_id": hall.theater_id})
    db.add(db_hall)
    db.commit()
    db.refresh(db_hall)

    # create seats: rows A.., at least 6 seats per row
    for r in range(num_rows):
        row_letter = chr(65 + r)
        for n in range(1, seats_per_row + 1):
            seat = models.Seat(row=row_letter, number=n, hall_id=db_hall.id)
            db.add(seat)
    db.commit()
    return db_hall

def list_halls(db: Session):
    return db.query(models.Hall).all()

# ---------- Shows ----------
def create_show(db: Session, show: schemas.ShowCreate):
    db_show = models.Show(**show.dict())
    db.add(db_show)
    db.commit()
    db.refresh(db_show)
    return db_show

def list_shows(db: Session):
    return db.query(models.Show).all()

# ---------- Seats ----------
def list_seats_by_hall(db: Session, hall_id: int):
    return db.query(models.Seat).filter(models.Seat.hall_id == hall_id).order_by(models.Seat.row, models.Seat.number).all()

# ---------- Users ----------
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def list_users(db: Session):
    return db.query(models.User).all()

# ---------- Bookings (single) ----------
def create_booking(db: Session, booking: schemas.BookingCreate):
    db_booking = models.Booking(**booking.dict())
    try:
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking
    except IntegrityError:
        db.rollback()
        return {"error": "Seat already booked for this show"}

def list_bookings(db: Session):
    return db.query(models.Booking).all()

def cancel_booking(db: Session, booking_id: int):
    b = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not b:
        return {"error": "Booking not found"}
    db.delete(b)
    db.commit()
    return {"message": f"Booking {booking_id} cancelled"}

# ---------- Group booking (consecutive seats) ----------
def book_consecutive_seats(db: Session, show_id: int, num_seats: int, user_id: int):
    """
    Try to find and book `num_seats` consecutive seats in the SAME row for the given show.
    Returns list of created Booking objects on success, else None.
    """
    # available seats for show (seat ids that are not booked for this show)
    # find all seats (with row, number) -> group by row
    # then search for consecutive numbers in same row
    all_seats = db.query(models.Seat).order_by(models.Seat.row, models.Seat.number).all()

    # booked seat ids for the show
    booked_ids = {r[0] for r in db.query(models.Booking.seat_id).filter(models.Booking.show_id == show_id).all()}

    rows = {}
    for s in all_seats:
        rows.setdefault(s.row, []).append(s)

    for row, seats in rows.items():
        # build list of available seat objects in this row (in order)
        avail = [s for s in seats if s.id not in booked_ids]
        # scan for consecutive groups by seat.number
        for i in range(0, len(avail) - num_seats + 1):
            group = avail[i:i+num_seats]
            expected = list(range(group[0].number, group[0].number + num_seats))
            if [s.number for s in group] == expected:
                # attempt booking transactionally
                bookings = []
                try:
                    for s in group:
                        b = models.Booking(user_id=user_id, show_id=show_id, seat_id=s.id)
                        db.add(b)
                        bookings.append(b)
                    db.commit()
                    for b in bookings:
                        db.refresh(b)
                    return bookings
                except IntegrityError:
                    db.rollback()
                    # concurrent race -> try continue or return failure
                    return None
    return None

# ---------- Group booking by seat ids (friends pick specific seats) ----------
def book_specific_seats(db: Session, user_id: int, show_id: int, seat_ids: list[int]):
    """
    Attempt to book list of specific seat_ids for a show for the user.
    Returns dict with keys: success (list), failed (list)
    Uses DB unique constraint + transaction to prevent double booking.
    """
    success = []
    failed = []
    for sid in seat_ids:
        b = models.Booking(user_id=user_id, show_id=show_id, seat_id=sid)
        db.add(b)
        try:
            db.commit()
            db.refresh(b)
            success.append(b)
        except IntegrityError:
            db.rollback()
            failed.append(sid)
    return {"success": success, "failed": failed}

# ---------- Suggest alternate shows where consecutive seats exist ----------
def suggest_alternate_shows_for_consecutive(db: Session, movie_id: int, num_seats: int):
    suggestions = []
    shows = db.query(models.Show).filter(models.Show.movie_id == movie_id).all()
    for s in shows:
        # count available consecutive spots
        bookings = {r[0] for r in db.query(models.Booking.seat_id).filter(models.Booking.show_id == s.id).all()}
        seats = db.query(models.Seat).order_by(models.Seat.row, models.Seat.number).all()
        rows = {}
        for seat in seats:
            rows.setdefault(seat.row, []).append(seat)
        found = False
        for row, row_seats in rows.items():
            avail = [seat for seat in row_seats if seat.id not in bookings]
            for i in range(0, len(avail) - num_seats + 1):
                group = avail[i:i+num_seats]
                expected = list(range(group[0].number, group[0].number + num_seats))
                if [s.number for s in group] == expected:
                    suggestions.append({"show_id": s.id, "time": s.time, "row": row, "start_number": group[0].number})
                    found = True
                    break
            if found:
                break
    return suggestions

# ---------- Seats availability ----------
def available_seats_for_show(db: Session, show_id: int):
    show = db.query(models.Show).filter(models.Show.id == show_id).first()
    if not show:
        return None
    all_seats = db.query(models.Seat).filter(models.Seat.hall_id == show.hall_id).order_by(models.Seat.row, models.Seat.number).all()
    booked = {r[0] for r in db.query(models.Booking.seat_id).filter(models.Booking.show_id == show_id).all()}
    avail = [s for s in all_seats if s.id not in booked]
    return avail

# ---------- Seat layout visualization ----------
def seat_layout_for_show(db: Session, show_id: int):
    show = db.query(models.Show).filter(models.Show.id == show_id).first()
    if not show:
        return None
    all_seats = db.query(models.Seat).filter(models.Seat.hall_id == show.hall_id).order_by(models.Seat.row, models.Seat.number).all()
    booked = {r[0] for r in db.query(models.Booking.seat_id).filter(models.Booking.show_id == show_id).all()}
    layout = {}
    for s in all_seats:
        layout.setdefault(s.row, {})[s.number] = ("Booked" if s.id in booked else "Available")
    # ascii map
    ascii_lines = []
    for row in sorted(layout.keys()):
        rowvals = "".join("[X]" if layout[row][n]=="Booked" else "[ ]" for n in sorted(layout[row].keys()))
        ascii_lines.append(f"{row} {rowvals}")
    return {"layout": layout, "ascii": "\n".join(ascii_lines)}

# ---------- User bookings ----------
def bookings_for_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    bookings = db.query(models.Booking).filter(models.Booking.user_id == user_id).all()
    result = []
    for b in bookings:
        show = db.query(models.Show).filter(models.Show.id == b.show_id).first()
        movie = db.query(models.Movie).filter(models.Movie.id == show.movie_id).first() if show else None
        seat = db.query(models.Seat).filter(models.Seat.id == b.seat_id).first()
        result.append({
            "booking_id": b.id,
            "movie_title": movie.title if movie else None,
            "show_id": b.show_id,
            "seat": f"{seat.row}{seat.number}" if seat else None
        })
    return {"user_id": user_id, "user_name": user.name, "bookings": result}

# ---------- Analytics ----------
def movie_analytics(db: Session, movie_id: int):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        return None
    total_tickets = db.query(func.count(models.Booking.id)).join(models.Show, models.Booking.show_id==models.Show.id).filter(models.Show.movie_id==movie_id).scalar()
    gmv = (total_tickets or 0) * (movie.price or 0)
    return {"movie_id": movie_id, "title": movie.title, "tickets_sold": total_tickets or 0, "gmv": float(gmv)}
