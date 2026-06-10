# Expense Tracker API

A REST API built with Python and Flask, backed by SQLite. 
Supports full CRUD for expense categories and individual expenses, 
with filtering by date, month, and year.

## Tech Stack
- Python
- Flask
- SQLite3

## Running Locally

1. Clone the repo
2. Install dependencies

pip install flask

3. Run the server
python app.py

4. API runs at `http://127.0.0.1:5000`

## Endpoints

### Categories
| Method | Endpoint | Description |
|---|---|---|
| GET | /categories | Get all categories |
| GET | /categories/<id> | Get one category |
| POST | /categories | Create a category |
| PUT | /categories/<id> | Update a category |
| DELETE | /categories/<id> | Delete a category |

### Expenses
| Method | Endpoint | Description |
|---|---|---|
| GET | /expenses | Get all expenses |
| GET | /expenses/<id> | Get one expense |
| GET | /expenses/date/<date> | Get expenses by date |
| GET | /expenses/month/<month> | Get expenses by month |
| GET | /expenses/year/<year> | Get expenses by year |
| POST | /expenses | Create an expense |
| PUT | /expenses/<id> | Update an expense |
| DELETE | /expenses/<id> | Delete an expense |

## What I Learned
- How to design and build a REST API from scratch
- Multi-table SQLite database design with foreign keys and CASCADE DELETE
- JOIN queries to combine data across tables
- Input validation and proper HTTP status codes
- Date validation and filtering with Python's datetime module
- Testing API endpoints with Postman