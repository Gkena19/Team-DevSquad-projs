from flask import Flask,render_template,request,redirect,url_for,flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'RunApp'

DATABASE = 'buildings.db'

def get_db_connection():
    """"Create database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with buildings table"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS buildings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            floors INTEGER NOT NULL,
            year_built INTEGER NOT NULL,
            building_code TEXT NOT NULL UNIQUE
        )   
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Displays all buildings"""
    conn = get_db_connection()
    buildings = conn.execute('SELECT * FROM buildings ORDER BY name').fetchall()
    conn.close()
    return render_template('index.html', buildings=buildings)

@app.route('/create', methods = ['GET','POST'])
def create_building():
    """Create a new building """
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        floors = request.form['floors']
        year_built = request.form['year_built']
        building_code = request.form['building_code']

        if not all([name,address,floors,year_built,building_code]):
            flash('All fields are required','error')
            return render_template('create.html')
        
        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO buildings(name, address, floors, year_built,building_code)
                VALUES(?,?,?,?,?)
            ''',(name,address,int(floors),int(year_built),building_code))
            conn.commit()
            conn.close()
            flash('Building created successfully','success')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('Building code already exists!','error')
        except ValueError:
            flash('Floors  and Year Built must be valid numbers','error')
         
    return render_template('create.html')

@app.route('/view/<int:id>')
def view_building(id):
    """view details of a specific building"""
    conn = get_db_connection()
    building = conn.execute('SELECT * FROM buildings WHERE id = ?',(id,)).fetchone()
    conn.close()

    if building is None:
        flash('Building not found!','error')
        return redirect(url_for('index'))
    
    return render_template('view.html', building=building)

@app.route('/update/<int:id>', methods = ['GET','POST'])
def update_building(id):
    """update an existing building"""
    conn = get_db_connection()
    building = conn.execute('SELECT * FROM buildings WHERE id =?',(id,)).fetchone()
    

    if building is None:
        conn.close()
        flash('Building not found!','error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        floors = request.form['floors']
        year_built = request.form['year_built']
        building_code = request.form['building_code']

        if not all([name,address,floors,year_built,building_code]):
            flash('All fields are required!','error')
            conn.close()
            return render_template('update.html', building=building)
    
        try:
            conn.execute('''
                UPDATE  buildings
                SET name = ?, address = ?, floors = ?, year_built = ?, building_code = ?
                WHERE id =?
            ''',(name, address, int(floors), int(year_built), building_code,id))
            conn.commit()
            flash('Building updated successfully','success')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash('Building code already exists','error')
        except ValueError:
            flash('Floors and Year Built must be valid numbers','error')
        
        finally:
            conn.close()
   
    return render_template('update.html', building=building)

@app.route('/delete/<int:id>')
def delete_building(id):
    """Delete a building"""
    conn = get_db_connection()
    building = conn.execute('SELECT * FROM buildings WHERE id = ?',(id,)).fetchone()

    if building is None:
        flash('Building not found!','error')
    else:
        conn.execute('DELETE FROM buildings WHERE id=?',(id,))
        conn.commit()
        flash('Building deleted successfully!','success')
        

    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
