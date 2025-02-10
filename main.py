from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext

app = FastAPI()


engine = create_engine("sqlite:///workout.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)


class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)

Base.metadata.create_all(bind=engine)


def add_dummy_exercises():
    db = SessionLocal()
    if not db.query(Exercise).first():  
        exercises = [
            Exercise(name="Push-ups", description="Strengthens chest and arms."),
            Exercise(name="Squats", description="Strengthens legs and glutes."),
            Exercise(name="Plank", description="Core stability exercise."),
            Exercise(name="Jump Rope", description="Good cardio workout."),
            Exercise(name="Pull-ups", description="Strengthens back and arms.")
        ]
        db.add_all(exercises)
        db.commit()
    db.close()

add_dummy_exercises()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    user = User(username=username, password=pwd_context.hash(password))
    db.add(user)
    db.commit()
    return {"message": "User registered"}


@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful"}


@app.get("/exercises")
def get_exercises(db: Session = Depends(get_db)):
    return db.query(Exercise).all()

@app.get("/")
def home():
    return {"message": "Welcome to Workout API"}
