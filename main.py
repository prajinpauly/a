from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, validator
from datetime import date
import mysql.connector

app = FastAPI()

def get_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="1234",
        database="finance"
    )

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if v.isdigit() or v.isalpha():
            raise ValueError('Password must contain both letters and numbers')
        return v

class LoginRequest(BaseModel):
    email: str
    password: str

class Expense(BaseModel):
    user_id: int
    amount: float
    date: date
    category_id: int
    note: str = None

@app.post("/signup")
def signup(user: SignupRequest):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
            (user.name, user.email, user.password)
        )
        db.commit()
        return {"message": "User registered successfully"}
    except mysql.connector.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    finally:
        cursor.close()
        db.close()

@app.post("/login")
def login(login: LoginRequest):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT user_id, password_hash FROM users WHERE email = %s", (login.email,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    if user and user["password_hash"] == login.password:  # For demo only!
        return {"user_id": user["user_id"]}
    else:
        raise HTTPException(status_code=401, detail="Invalid email or password")

@app.get("/categories/")
def get_categories():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT category_id, name, type FROM categories")
    categories = cursor.fetchall()
    cursor.close()
    db.close()
    return categories

@app.post("/expenses/")
def add_expense(exp: Expense):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO transactions (user_id, amount, date, category_id, note) VALUES (%s, %s, %s, %s, %s)",
            (exp.user_id, exp.amount, exp.date, exp.category_id, exp.note)
        )
        db.commit()
        return {"message": "Expense added", "date": str(exp.date)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        db.close()

@app.get("/expenses/{user_id}")
def get_expenses(user_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions WHERE user_id = %s", (user_id,))
    expenses = cursor.fetchall()
    cursor.close()
    db.close()
    return expenses

@app.delete("/expenses/{transaction_id}")
def delete_expense(transaction_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM transactions WHERE transaction_id=%s", (transaction_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Expense deleted"}