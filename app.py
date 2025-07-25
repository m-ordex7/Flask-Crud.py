from flask import Flask, render_template, request, url_for, flash, redirect
from flask_mysqldb import MySQL
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'some_random_data')  # Use environment variable for secret key

# MySQL configurations from environment variables
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'inventory')

mysql = MySQL(app)

@app.route('/')
def index():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM inventory")
        data = cursor.fetchall()
        cursor.close()
        return render_template('index.html', drinks=data)
    except Exception as e:
        flash(f"Error fetching data: {str(e)}", "error")
        return render_template('index.html', drinks=[])
@app.route('/insert', methods=['POST'])
def insert():
    if request.method == "POST":
        try:
            # Retrieve form data
            name = request.form['name_of_drink'].strip()
            price = request.form['price']
            quantity = request.form['quantity']
            expiry_date = request.form['expiry_date']
            batch_no = request.form['batch_no'].strip()
            drink_subtype = request.form['drink_subtype'].strip()

            # Input validation
            if not name or not batch_no or not drink_subtype:
                flash("Name, batch number, and drink subtype cannot be empty.", "error")
                return redirect(url_for('index'))

            try:
                price = float(price)
                if price < 0:
                    flash("Price cannot be negative.", "error")
                    return redirect(url_for('index'))
            except ValueError:
                flash("Price must be a valid number.", "error")
                return redirect(url_for('index'))

            try:
                quantity = int(quantity)
                if quantity < 0:
                    flash("Quantity cannot be negative.", "error")
                    return redirect(url_for('index'))
            except ValueError:
                flash("Quantity must be a valid integer.", "error")
                return redirect(url_for('index'))

            try:
                datetime.strptime(expiry_date, '%Y-%m-%d')
            except ValueError:
                flash("Invalid expiry date format. Use YYYY-MM-DD.", "error")
                return redirect(url_for('index'))

            # Insert data into the database
            cursor = mysql.connection.cursor()
            cursor.execute(
                """INSERT INTO inventory (name_of_drink, price, quantity, expiry_date, batch_no, drink_subtype)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (name, price, quantity, expiry_date, batch_no, drink_subtype)
            )
            mysql.connection.commit()
            cursor.close()
            flash("Drink added successfully!", "success")
            return redirect(url_for('index'))

        except Exception as e:
            mysql.connection.rollback()  # Rollback in case of error
            flash(f"Error inserting data: {str(e)}", "error")
            return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        try:
            name = request.form['name_of_drink'].strip()
            price = request.form['price']
            quantity = request.form['quantity']
            expiry_date = request.form['expiry_date']
            batch_no = request.form['batch_no'].strip()
            drink_subtype = request.form['drink_subtype'].strip()

            cursor.execute("""
                UPDATE inventory
                SET name_of_drink=%s, price=%s, quantity=%s, expiry_date=%s, batch_no=%s, drink_subtype=%s
                WHERE id=%s
            """, (name, price, quantity, expiry_date, batch_no, drink_subtype, id))
            mysql.connection.commit()
            flash("Drink updated successfully!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error updating drink: {str(e)}", "error")
            return redirect(url_for('index'))
    else:
        cursor.execute("SELECT * FROM inventory WHERE id = %s", (id,))
        drink = cursor.fetchone()
        cursor.close()
        return render_template('edit.html', drink=drink)

@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM inventory WHERE id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        flash("Drink deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting drink: {str(e)}", "error")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
