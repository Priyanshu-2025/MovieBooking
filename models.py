from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True, nullable=False)
    price = Column(Float, nullable=False)  # price per ticket
    shows = relationship("Show", back_populates="movie", cascade="all, delete-orphan")

class Theater(Base):
    __tablename__ = "theaters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    halls = relationship("Hall", back_populates="theater", cascade="all, delete-orphan")

class Hall(Base):
    __tablename__ = "halls"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    theater_id = Column(Integer, ForeignKey("theaters.id"))
    theater = relationship("Theater", back_populates="halls")
    shows = relationship("Show", back_populates="hall", cascade="all, delete-orphan")
    seats = relationship("Seat", back_populates="hall", cascade="all, delete-orphan")

class Show(Base):
    __tablename__ = "shows"
    id = Column(Integer, primary_key=True, index=True)
    time = Column(String, nullable=False)  # keep as string for simplicity (e.g., "12:00")
    movie_id = Column(Integer, ForeignKey("movies.id"))
    hall_id = Column(Integer, ForeignKey("halls.id"))
    movie = relationship("Movie", back_populates="shows")
    hall = relationship("Hall", back_populates="shows")
    bookings = relationship("Booking", back_populates="show", cascade="all, delete-orphan")

class Seat(Base):
    __tablename__ = "seats"
    id = Column(Integer, primary_key=True, index=True)
    row = Column(String, nullable=False)   # e.g., "A"
    number = Column(Integer, nullable=False)  # e.g., 1
    hall_id = Column(Integer, ForeignKey("halls.id"))
    hall = relationship("Hall", back_populates="seats")

    # unique seat in a hall by row+number
    __table_args__ = (
        UniqueConstraint("hall_id", "row", "number", name="unique_seat_in_hall"),
    )

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    show_id = Column(Integer, ForeignKey("shows.id"))
    seat_id = Column(Integer, ForeignKey("seats.id"))

    user = relationship("User", back_populates="bookings")
    show = relationship("Show", back_populates="bookings")
    seat = relationship("Seat")

    # prevent double-booking a seat for the same show at DB level
    __table_args__ = (
        UniqueConstraint("show_id", "seat_id", name="unique_show_seat_booking"),
    )
