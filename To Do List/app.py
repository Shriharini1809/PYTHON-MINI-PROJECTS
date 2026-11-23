from flask import Flask,render_template,request,jsonify
import mysql.connector

app = Flask(__name__)

DB_CONFIG = {"host":"localhost","user":"root","password":"shri","port":3306}
connection = None
cursor = None

try:
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("create database if not exists todo_list")
    cursor.execute("use todo_list")
    cursor.execute("""
                    create table if not exists tasks(id INT PRIMARY KEY AUTO_INCREMENT,task varchar(50),status boolean default 0,created_at date default (CURRENT_DATE));
                   """)
    cursor.close()
    connection.close()
    
    print("Database created successfully")
    print("Table created successfully")

except mysql.connector.Error as error:
    print("MySQL error: ",error)

@app.route("/")
@app.route("/index",methods=["GET","POST"])
def index():
    try:
        if request.method == 'POST':
            addtask = request.form["addtask"]
            
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            cursor.execute("use todo_list")
            query = "insert into tasks(task) values(%s)"
            value = (addtask,)
            cursor.execute(query,value)
            connection.commit()
            cursor.close()
            connection.close()
    
    except mysql.connector.Error as error:
        print("MYSQL error: ",error)
        
        
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    cursor.execute("use todo_list")
    
    cursor.execute("select * from tasks")
    result = cursor.fetchall()
    
    cursor.execute("select count(*) from tasks")
    all = cursor.fetchone()
    
    cursor.execute("select count(*) from tasks where status = 0")
    pending = cursor.fetchone()
    
    cursor.execute("select count(*) from tasks where status = 1")
    completed= cursor.fetchone()
           
    return render_template("index.html",task = result,count = all,pending=pending,completed=completed)


@app.route("/update-task/<int:task_id>", methods=["POST"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    updated_task = data.get("task" ,"").strip()
    if not updated_task:
        return jsonify({"message":"Task cannot be empty!"}),400
    if len(updated_task) > 50:
        return jsonify({
            "message":"Task must be below 50 character!!"
        }),400
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor=connection.cursor()
        cursor.execute("select id from todo_list.tasks where id = %s",
                       (task_id,))
        if cursor.fetchone() is None:
            return jsonify({
                "message" : "Task not found!!"
            }),404
            
        query = "update todo_list.tasks set task = %s where id = %s"
        values = (updated_task,task_id)
        
        cursor.execute(query,values)
        
        connection.commit()
        
        return jsonify({
            "message" : "Task updated successfully!!"
        }),200
    
    except mysql.connector.Error as error:
        print("MySQL error:", error)

        return jsonify({
            "message": "Database update failed!"
        }), 500
        
        
    finally:
        if cursor:
            cursor.close()
        
        if connection and connection.is_connected():
            connection.close()
    

@app.route("/delete-task/<int:task_id>",methods=["POST"])
def delete_task(task_id):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        cursor.execute("select id from todo_list.tasks where id = %s",(task_id,))
        if cursor.fetchone() is None:
            return jsonify({"message":"Task not found!!"}),404
        
        query = "delete from todo_list.tasks where id = %s"
        value = (task_id,)
        cursor.execute(query,value)
        
        connection.commit()
        
        return jsonify({"message":"Task deleted Successfully!"}),200
    
    except mysql.connector.Error as error:
        print("MySQL error: ",error)
        return jsonify({"message":"Database delete failed!"}),500
    
    finally:
        if cursor:
            cursor.close()
        
        if connection and connection.is_connected():
            connection.close

    
    
@app.route("/toggle-task/<int:task_id>", methods=["POST"])
def toggle_task(task_id):

    # Get status from JavaScript
    data = request.get_json(silent=True) or {}

    new_status = data.get("status")

    # Validate status
    if new_status not in [0, 1]:
        return jsonify({
            "message": "Invalid task status!"
        }), 400

    connection = None
    cursor = None

    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Check whether task exists
        cursor.execute(
            "SELECT id FROM todo_list.tasks WHERE id = %s",
            (task_id,)
        )

        if cursor.fetchone() is None:
            return jsonify({
                "message": "Task not found!"
            }), 404

        # Update task status
        query = """
            UPDATE todo_list.tasks
            SET status = %s
            WHERE id = %s
        """

        values = (new_status, task_id)

        cursor.execute(query, values)

        # Save changes
        connection.commit()

        return jsonify({
            "message": "Task status updated successfully!",
            "status": new_status
        }), 200

    except mysql.connector.Error as error:

        print("MySQL error:", error)

        return jsonify({
            "message": "Database update failed!"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    app.run(debug=True)