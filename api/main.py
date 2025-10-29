# FastAPI is a Python library that 
# allows us to 
# - take in a request (from the client)
# - send back a response
# Note we also need body parser for POST requests
from fastapi import FastAPI, Body

# CORS (Cross-Origin Resource Sharing)
# allows us to restrict/enable 
# which client urls are allowed 
# to send requests to this backend code.
from fastapi.middleware.cors import CORSMiddleware

# this library allows Python to speak with Postgres
# and to return database query results in JSON format
import psycopg2
from psycopg2.extras import RealDictCursor

import os  # to access the DATABASE_URL from Vercel

# Database connection


# Create table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS items (
    item_id SERIAL PRIMARY KEY,
    item_name TEXT NOT NULL,
    item_desc TEXT NOT NULL
)
""")
conn.commit()


# Initialize the FastAPI application
app = FastAPI(
    title="FastAPI Example",
    description="This is an example of using FastAPI with Postgres"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # can have your front-end url to secure API use
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Route Definitions

# default route
@app.get("/")           #endpoint, or route, always starts with a forward slash
def default_route():    #route handler function
    """
    This is the default endpoint for this back-end.
    """
    return "You have reached the default route. Back-end server is listening..."


# other routes go here, possibly including 
# some SQL to run against the database
# e.g. INSERT, SELECT, UPDATE, DELETE
  
# this GET route selects all the records from a database table
@app.get("/items")
def select_all_item_records():
    """
    GET all records from database table
    """
    cur = conn.cursor(cursor_factory=RealDictCursor)  # return result as JSON
    cur.execute("SELECT * FROM items")
    data = cur.fetchall()
    return data    


# this POST route inserts a new record in a database table
@app.post("/item")
def insert_new_item_record(new_item_name = Body(...), new_item_desc = Body(...),):    
    """
    POST a record to database table
    """
    cur.execute("INSERT INTO items (item_name,item_desc) VALUES (%s,%s)", (new_item_name, new_item_desc) ) 
    conn.commit()
    return {"success":True, "message": "new record added"}


# Usage notes:
# 1. Put this code in api/main.py and deploy as a Vercel project
# 2. Make sure you have a database connected to the Vercel project
# 3. Test by using your-vercel-backend-url/docs
# 4. Later call from front-end using JavaScript fetch()