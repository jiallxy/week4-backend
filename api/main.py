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
from fastapi.responses import RedirectResponse

import hashlib  # used to generate a unique hash value for the short code
import os        # to access the DATABASE_URL from Vercel

import psycopg2
from psycopg2.extras import RealDictCursor  # to return response as json objects

# Database connection
conn = psycopg2.connect( os.environ.get("DATABASE_URL") )
cur = conn.cursor()

# Create table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS urls (
    shortCode TEXT PRIMARY KEY,
    longUrl TEXT NOT NULL,
    urlDesc TEXT NOT NULL
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

# Route (or Endpoint) Definitions
# default route
@app.get("/")
def root():
    return {"message": "backend server with database is running"}


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
# create a short url
@app.post("/shorten")
def shorten_url(longUrl = Body(...), urlDesc = Body(...)):
    shortCode = hashlib.md5(longUrl.encode()).hexdigest()[:10]  
    cur.execute("INSERT INTO urls (shortCode, longUrl, urlDesc) VALUES (%s, %s, %s)", (shortCode, longUrl, urlDesc))
    conn.commit()
    return {"shortCode": shortCode}


# get all short urls
# this GET route needs to be first
@app.get("/urls")
def get_all_urls():
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM urls")
    data = cur.fetchall()
    return data    

# re-direct the short url to the original long one
@app.get("/{shortCode}")
def get_long_url(shortCode):
    cur.execute("SELECT longUrl,urlDesc FROM urls WHERE shortCode = %s", (shortCode,))
    result = cur.fetchone()

    # print(f">>>>>>>>> got from db: {result[0]} {result[1]}")

    if result:
        return RedirectResponse(url=result[0]) #{ "longUrl": result[0], "urlDesc": result[1] }
    return {"error": "URL not found"}



# Usage notes:
# 1. Put this code in api/main.py and deploy as a Vercel project
# 2. Make sure you have a database connected to the Vercel project
# 3. Test by using your-vercel-backend-url/docs
# 4. Later call from front-end using JavaScript fetch()
    