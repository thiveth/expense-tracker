from flask import Flask, request, jsonify
import datetime as dt
import sqlite3

con = sqlite3.connect("expense_tracker.db")
cur = con.cursor()
cur.execute("PRAGMA foreign_keys = ON")
cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
            
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            budget REAL NOT NULL
            )
        """)

cur.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
            
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
            )
        """)
con.commit()
con.close()

app = Flask(__name__)

@app.route("/categories", methods=['GET'])
def get_categories():
    con = sqlite3.connect("expense_tracker.db")
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    categories_dict = {"categories": []}

    
    result = cur.execute("SELECT * FROM categories").fetchall()

    if not result:
        con.close()
        return jsonify({"error": "no categories exist"}), 400
    else:
        try:
            for row in result:
                categories_dict["categories"].append({"id": row[0], "name": row[1], "budget": row[2]})
            con.close()
            return jsonify({"status": 200,
                                "count": len(result),
                                "categories": categories_dict["categories"]}), 200
        except Exception as e:
            con.close()
            return jsonify({"error": f"{str(e)}"}), 400
    
@app.route("/categories/<int:id>", methods=['GET'])
def get_category(id):
    con = sqlite3.connect("expense_tracker.db")
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    
    result = cur.execute("SELECT id, name, budget FROM categories WHERE id = ?", (id,)).fetchone()
    if not result:
        con.close()
        return jsonify({"error": f"category doesn't exist"}), 404
    
    con.close()
    return jsonify({"status": 200,
    
                    "id": result[0],
                    "name": result[1],
                    "budget": result[2]}), 200

@app.route('/categories', methods=['POST'])
def create_category():
    con = sqlite3.connect("expense_tracker.db")
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    data = request.get_json()
    count = 0
    invalid_rows = 0

    ## {"categories": [{"name": str, "budget": float},
    ##                 {"name": str, "budget": float}""]}

    if "categories" in data and type(data["categories"]) == list:
        for row in data["categories"]:
            if ("name" in row and "budget" in row) and (type(row["name"]) == str and (type(row["budget"]) == int or type(row["budget"])==float)):               
                try: 
                    row["name"] = row["name"].capitalize()
                    cur.execute("INSERT INTO categories (name, budget) VALUES (?, ?)", (row["name"], row["budget"]))
                except sqlite3.IntegrityError:
                    invalid_rows +=1
                    continue    
            else:
                return jsonify({"error": "invalid queries passed"})    
        
        if invalid_rows == len(data["categories"]):
            con.close()
            return jsonify({"error": "categories already exist"}), 400
        
        count = len(data["categories"]) - invalid_rows
        con.commit()
        con.close()
        return jsonify({"status": 201,
                    "count": count}), 201

    if "name" not in data or "budget" not in data:
        return jsonify({"error": "name or budget not passed"}), 400
    elif type(data["name"]) != str or (type(data["budget"]) != int and type(data["budget"]) != float):
         con.close()
         return jsonify({"error": "invalid types passed"}), 400
    elif data["name"] is None or data["budget"] is None:
        con.close()
        return jsonify({"error": "name or budget not passed"}), 400
    
    try:
        data["name"] = data["name"].capitalize()
        cur.execute("INSERT INTO categories (name, budget) VALUES (?, ?)", (data["name"], data["budget"]))
    except sqlite3.IntegrityError:
        return jsonify({"status": 400, "error": "category already exists"}), 400
    else:
        count = cur.rowcount
        con.commit()
        con.close()
        return jsonify({"status": 201,
                        "count": count}), 201

@app.route("/categories/<int:id>", methods=['PUT'])
def update_category(id):
    con = sqlite3.connect("expense_tracker.db")
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    result = cur.execute("SELECT * FROM categories where id = ?", (id,)).fetchone()

    if not result:
        con.close()
        return jsonify({"error": "category doesn't exist"}), 404
    
    data = request.get_json()
    print(data)

    if "name" not in data and "budget" not in data:
        return jsonify({"error": "invalid queries passed"}), 400
    elif ("name" in data and "budget" not in data) and (type(data["name"]) == str):
        data["name"] = data["name"].capitalize()
        cur.execute("UPDATE categories SET name = ? WHERE id = ?",(data["name"], id))
        con.commit()
    elif ("budget" in data and "name" not in data) and (type(data["budget"]) == int or (type(data["budget"]) == float)):
        cur.execute("UPDATE categories SET budget = ? WHERE id = ?", (data["budget"], id))
        con.commit()
    elif ("budget" in data and "name" in data) and ((type(data["name"]) == str) and (type(data["budget"]) == int or (type(data["budget"]) == float))):
        cur.execute("UPDATE categories SET name = ?, budget = ? WHERE id = ?", (data["name"], data["budget"], id))
        con.commit()
    else:
        con.close()
        return jsonify({"error": "invalid queries passed"}), 400

    
    count = cur.rowcount
    con.close()
    return jsonify({"status": 200,
                    "count": count}), 200
    
@app.route("/categories/<int:id>", methods=['DELETE'])
def delete_category(id):
    con = sqlite3.connect("expense_tracker.db")
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    cur.execute("DELETE FROM categories WHERE id = ?", (id,))

    if cur.rowcount == 1:
        con.commit()
        con.close()
        return jsonify({"status": 200,
                        "message": f"category {id} removed"}), 200
    else:
        con.commit()
        con.close()
        return jsonify({"error": "category not found"}), 404
    

## Expenses

''' SELECT expenses.id, expenses.name, expenses.amount,
    expenses.date, categories.name FROM expenses JOIN categories ON 
    expenses.category_id = categories.id
'''


@app.route("/expenses", methods=['GET'])
def get_expenses():
    con = sqlite3.connect("expense_tracker.db")
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    expense_dict = {"expenses": []}

    result = cur.execute("SELECT expenses.id, expenses.name, expenses.amount, expenses.date, expenses.category_id, categories.name FROM expenses JOIN categories ON expenses.category_id = categories.id").fetchall()

    if not result:
        con.close()
        return jsonify({"error": "no expenses exist"}), 404

    for _ in result:
        expense_dict["expenses"].append({"id": _[0],
                                         "name": _[1],
                                         "amount": _[2],
                                         "date": _[3],
                                         "category_id": _[4],
                                         "category_name": _[5]})
    
    con.close()
    return jsonify({"status": 200,
                    "count": len(result),
                    "expenses": expense_dict["expenses"]}), 200



@app.route("/expenses/<int:id>", methods=['GET'])
def get_expense(id):
    con = sqlite3.connect("expense_tracker.db")
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    try:
        (int(id))
    except ValueError:
        return jsonify({"error": "invalid id format"}), 400
    try:
        result = cur.execute("SELECT expenses.id, expenses.name, expenses.amount, expenses.date, expenses.category_id, categories.name FROM expenses JOIN categories ON expenses.category_id = categories.id WHERE expenses.id = ?", (int(id),)).fetchone()
    except sqlite3.OperationalError as e:
        con.close()
        return jsonify({"error": "database error"}), 500
    else:
        if not result:
            con.close()
            return jsonify({"error": "no expense found"}), 404
        else:
            con.close()
            return jsonify({"status": 200,
                            
                            "id": result[0],
                            "name": result[1],
                            "amount": result[2],
                            "date": result[3],
                            "category_id": result[4],
                            "category_name": result[5]}), 200
            
@app.route("/expenses/date/<date>", methods=['GET'])
def get_expenses_by_date(date):
    con = sqlite3.connect("expense_tracker.db")
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    print(date)
    
    try:
        dt.date.fromisoformat(date)
    except Exception as e:
        con.close()
        return jsonify({"error": f"an error occured {str(e)}"}), 400
    
    result = cur.execute("SELECT expenses.id, expenses.name, expenses.amount, expenses.date, expenses.category_id, categories.name FROM expenses JOIN categories ON expenses.category_id = categories.id WHERE expenses.date = ? ", (date,)).fetchall()

    if not result:
        con.close()
        return jsonify({"error": "no expenses with this date"}), 404
    
    expenses_dict = {"expenses": []}

    for _ in result:
        expenses_dict["expenses"].append({"id": _[0],
                                        "name": _[1],
                                        "amount": _[2],
                                        "date": _[3],
                                        "category_id": _[4],
                                        "category_name": _[5]})

    con.close()
    return jsonify({"status": 200,
                    "count": len(result),
                    "expenses": expenses_dict["expenses"]}), 200
    
    


@app.route("/expenses/month/<month>", methods=['GET'])
def get_expenses_by_month(month):
    con = sqlite3.connect("expense_tracker.db")
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    valid_months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

    if month not in valid_months:
        con.close()
        return jsonify({"error": "invalid queries passed"}), 404
    
    expenses = {"expenses": []}
    
    result = cur.execute(f"SELECT expenses.id, expenses.name, expenses.amount, expenses.date, expenses.category_id, categories.name FROM expenses JOIN categories ON expenses.category_id = categories.id WHERE expenses.date LIKE '%-{month}-%'").fetchall()
    if not result:
        return jsonify({"error": "no expenses match this month"}), 404
    
    for item in result:
        expenses["expenses"].append({"id": item[0],
                                        "name": item[1],
                                        "amount": item[2],
                                        "date": item[3],
                                        "category_id": item[4],
                                        "category_name": item[5],})
        
    con.close()
    return jsonify({"status": 200,
                    "expenses": expenses["expenses"]}), 200

    

@app.route("/expenses/year/<year>", methods=['GET'])
def get_expenses_by_year(year):
    con = sqlite3.connect("expense_tracker.db")
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    min_year = 2026
    max_year = min_year + 1

    try:
        int(year)
    except TypeError:
        con.close()
        return jsonify({"error": "invalid query passed"}), 404
    except ValueError:
        con.close()
        return jsonify({"error": "invalid query passed"}), 404
    
    if int(year) < min_year:
        con.close()
        return jsonify({"error": "year out of range"}), 400
    
    start_date = dt.date(int(year), 1, 1)
    end_date = dt.date(max_year, 1, 1)
    #print(end_date)
    expense_dict = {"expenses": []}
    
    # print(cur.execute("SELECT date FROM expenses LIMIT 1").fetchone())
    years_query = cur.execute("SELECT expenses.id, expenses.name, expenses.amount, expenses.date, expenses.category_id, categories.name FROM expenses JOIN categories ON expenses.category_id = categories.id WHERE expenses.date >= ? AND expenses.date < ?", (start_date, end_date)).fetchall()
    
    if not years_query:
        con.close()
        return jsonify({"error": "no expenses match this query"}), 404
    
    for expense in years_query:
        expense_dict["expenses"].append({"id": expense[0],
                                         "name": expense[1],
                                         "amount": expense[2],
                                         "date": expense[3],
                                         "category_id": expense[4],
                                         "category_name": expense[5]})

    con.close()
    return jsonify({"status": 200,
                    "expenses": expense_dict["expenses"]}), 200


@app.route("/expenses", methods=['POST'])
def create_expense():
    con = sqlite3.connect("expense_tracker.db")
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    data = request.get_json()
    

    if ("name" not in data) or ("amount" not in data) or ("date" not in data) or ("category_id" not in data):
        return jsonify({"error": "missing crucial parameter"}), 400
    elif type(data["name"]) != str or (type(data["amount"]) != int and type(data["amount"]) != float) or type(data["date"]) != str or type(data["category_id"]) != int:
        return jsonify({"error": "invalid queries passed"}), 400
    
        
    try:
        dt.date.fromisoformat(data["date"])
    except ValueError:
        con.close()
        return jsonify({"error": "invalid date format"}), 400
    else:
        formatted_date = dt.date.fromisoformat(data["date"]).strftime("%Y-%m-%d")
        try:
            cur.execute("INSERT INTO expenses (name, amount, date, category_id) VALUES (?, ?, ?, ?)", (data["name"], data["amount"], formatted_date, data["category_id"]))
        except sqlite3.OperationalError:
            con.close()
            return jsonify({"error": "category_id value doesn't exist"}), 400
        except sqlite3.IntegrityError:
            con.close()
            return jsonify({"error": "category_id value doesn't exist"}), 400
        else:
            count = cur.rowcount
            con.commit()
            con.close()
            return jsonify({"status": 201,
                            "count": count}), 201
            
@app.route("/expenses/<int:id>", methods=['PUT'])
def update_expense(id):
    con = sqlite3.connect("expense_tracker.db")
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    valid_entries = ["name", "amount", "date", "category_id"]
    
    try:
        int(id)
    except Exception:
        con.close()
        return jsonify({"error": "invalid format"}), 400
    
    expense_exists = cur.execute("SELECT name, amount, date, category_id FROM expenses WHERE id = ?", (id,)).fetchone()

    if not expense_exists:
        con.close()
        return jsonify({"error": "expense does not exist"}), 404
    
    expense_name, expense_amount, expense_date, expense_category_id = expense_exists

    data = request.get_json()

    if not data:
        con.close()
        return jsonify({"error": "missing request body"}), 400
    
    if "amount" in data:
        amount = data["amount"]
        
        if not int(amount) or not float(amount):
            con.close()
            return jsonify({"error": "amount must be a positive value"}), 400
        
    if "name" in data:
        new_name = data["name"]
        if not new_name:
            con.close()
            return jsonify({"name cannot be empty"}), 400
        if type(new_name) != str:
            con.close()
            return jsonify({"invalid name type passed"}), 400
        new_name = new_name.strip()
        if new_name == expense_name:
            con.close()
            return jsonify({"error": f"the expense name is already '{new_name}'"}), 400

    if "date" in data:
        min_year = 2026
        date_str = data["date"]
        min_date = dt.date(min_year, 1, 1)
        try:
            parsed_date = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
            if parsed_date < min_date or parsed_date > dt.date.today():
                con.close()
                return jsonify({"error": "invalid date passed"}), 400
        except ValueError:
            con.close()
            return jsonify({"error": "date must be in 'YYYY-MM-DD' format"}), 400
        
        if parsed_date == expense_date:
            con.close()
            return jsonify({"error": f"expense date already matches '{parsed_date}'"}), 400
            
    if "category_id" in data:
        cat_id = data["category_id"]
        if (type(cat_id)) != int:
            con.close()
            return jsonify({"error": "invalid category_id passed"}), 400
        category_exists = cur.execute("SELECT id FROM categories WHERE id = ?", (cat_id,)).fetchone()
        if not category_exists:
            con.close()
            return jsonify({"error": f"category_id '{cat_id}' does not exist"}), 400

    fields_to_update = []
    params = []

    for item in valid_entries:
        if item in data:
            fields_to_update.append(f"{item} = ?")
            val = str(data[item]).strip() if item == "name" else data[item]
            params.append(val)
    params.append(id)
    
    if not fields_to_update:
        con.close()
        return jsonify({"error": "no valid fields to update"}), 400
    
    
    query = f"UPDATE expenses SET {', '.join(fields_to_update)} WHERE id = ?"
    print(query)
    print(params)
    print(tuple(params), 1)
    cur.execute(query, tuple(params))
    count = cur.rowcount
    con.commit()
    con.close()

    return jsonify({"status": 200,
                    "count": count}), 200



@app.route("/expenses/<id>", methods=['DELETE'])
def delete_expense(id):
    con = sqlite3.connect("expense_tracker.db")
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    try:
        int(id)
    except Exception:
        con.close()
        return jsonify({"error": "invalid query passed"}), 404
    
    result = cur.execute("DELETE FROM expenses WHERE id = ?", (id,))
    con.commit()

    if result.rowcount == 1:
        con.close()
        return jsonify({"status": 200,
                   "count": result.rowcount}), 200

    con.close()
    return jsonify({"error": "no expense matches id"}), 404


if __name__ == '__main__':
    app.run(debug=True)