from flask import Flask, render_template, request, redirect
import sqlite3

from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


#app = Flask(__name__)

# Create database table
def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            status TEXT,
            image TEXT
        )
    ''')
    conn.close()

init_db()

@app.route('/')
def home():
    search = request.args.get('search')
    status_filter = request.args.get('status')

    conn = sqlite3.connect('database.db')

    query = "SELECT * FROM items WHERE 1=1"
    params = []

    if search and search.strip():
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend(['%' + search + '%', '%' + search + '%'])

    if status_filter and status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)

    items = conn.execute(query, params).fetchall()

     # ✅ ADD THESE 4 LINES HERE
    total = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    lost = conn.execute("SELECT COUNT(*) FROM items WHERE status='Lost'").fetchone()[0]
    found = conn.execute("SELECT COUNT(*) FROM items WHERE status='Found'").fetchone()[0]
    claimed = conn.execute("SELECT COUNT(*) FROM items WHERE status='Claimed'").fetchone()[0]

    conn.close()
    conn.close()

    return render_template("index.html", items=items,  total=total,
                           lost=lost,
                           found=found,
                           claimed=claimed)



@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        image = request.files['image']
        filename = None

        if image and image.filename != '':
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = sqlite3.connect('database.db')
        conn.execute(
            "INSERT INTO items (title, description, status, image) VALUES (?, ?, ?, ?)",
            (title, description, status, filename)
        )
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("add_item.html")


# ✅ ADD DELETE ROUTE HERE
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('database.db')
    conn.execute("DELETE FROM items WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/claim/<int:id>')
def claim(id):
    conn = sqlite3.connect('database.db')
    conn.execute("UPDATE items SET status = 'Claimed' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect('database.db')

    item = conn.execute("SELECT * FROM items WHERE id = ?", (id,)).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']

        conn.execute(
            "UPDATE items SET title = ?, description = ?, status = ? WHERE id = ?",
            (title, description, status, id)
        )
        conn.commit()
        conn.close()
        return redirect('/')

    conn.close()
    return render_template("edit_item.html", item=item)



if __name__ == '__main__':
    app.run(debug=True)
