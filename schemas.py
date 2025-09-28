from pydantic import BaseModel
from typing import Optional, List

# Movie
class MovieBase(BaseModel):
    title: str
    price: float

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int
    class Config:
        orm_mode = True

# Theater
class TheaterBase(BaseModel):
    name: str

class TheaterCreate(TheaterBase):
    pass

class Theater(TheaterBase):
    id: int
    class Config:
        orm_mode = True

# Hall
class HallBase(BaseModel):
    name: str
    theater_id: int

class HallCreate(HallBase):
    # optional layout parameters could be added later
    pass

class Hall(HallBase):
    id: int
    class Config:
        orm_mode = True

# Show
class ShowBase(BaseModel):
    time: str
    movie_id: int
    hall_id: int

class ShowCreate(ShowBase):
    pass

class Show(ShowBase):
    id: int
    class Config:
        orm_mode = True

# Seat
class SeatBase(BaseModel):
    row: str
    number: int
    hall_id: int

class SeatCreate(SeatBase):
    pass

class Seat(SeatBase):
    id: int
    class Config:
        orm_mode = True

# User
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

# Booking
class BookingBase(BaseModel):
    user_id: int
    show_id: int
    seat_id: int

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    class Config:
        orm_mode = True

# Group booking request
class GroupBookingRequest(BaseModel):
    user_id: int
    show_id: int
    num_seats: int

# Group seats booking by exact seat ids (friends pick seats)
class GroupSeatBookingRequest(BaseModel):
    user_id: int
    show_id: int
    seat_ids: List[int]
