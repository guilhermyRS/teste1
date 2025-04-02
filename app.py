from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Configuração inicial do banco de dados
def init_db():
    with sqlite3.connect("finance.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,  -- "receita" ou "despesa"
                amount REAL NOT NULL,
                description TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

# Função para calcular os totais
def get_financial_summary():
    with sqlite3.connect("finance.db") as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'receita'")
        total_income = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'despesa'")
        total_expense = cursor.fetchone()[0] or 0

    balance = total_income - total_expense
    return total_income, total_expense, balance

@app.route("/")
def index():
    total_income, total_expense, balance = get_financial_summary()
    with sqlite3.connect("finance.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
        transactions = cursor.fetchall()
    
    return render_template("index.html", transactions=transactions, total_income=total_income, total_expense=total_expense, balance=balance)

@app.route("/add", methods=["GET", "POST"])
def add_transaction():
    if request.method == "POST":
        transaction_type = request.form["type"]
        amount = float(request.form["amount"])
        description = request.form["description"]

        with sqlite3.connect("finance.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO transactions (type, amount, description) VALUES (?, ?, ?)", 
                           (transaction_type, amount, description))
            conn.commit()
        
        return redirect(url_for("index"))

    return render_template("add_transaction.html")

@app.route("/delete/<int:id>")
def delete_transaction(id):
    with sqlite3.connect("finance.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (id,))
        conn.commit()
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
