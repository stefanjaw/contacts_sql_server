'''
Installation from CLI

pip install pyodbc
pip install flask

'''
# Global Vars
server_name = "localhost"
database_name = "test"
database_username = "sa"
database_password = "123456"


import pyodbc
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# HTML template for displaying contacts
# Uses Tailwind CSS for basic styling.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact List</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
    </style>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen p-4">
    <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-4xl">
        <h1 class="text-3xl font-bold text-gray-800 mb-6 text-center">Your Contacts</h1>

        {% if contacts %}
            <div class="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider rounded-tl-lg">ID</th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider rounded-tr-lg">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {% for contact in contacts %}
                            <tr class="hover:bg-gray-50">
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 rounded-bl-lg">{{ contact.id }}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{{ contact.name }}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{{ contact.phone }}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{{ contact.email }}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700 rounded-br-lg">
                                    <a href="/edit/{{ contact.id }}" class="text-indigo-600 hover:text-indigo-900 mr-4 font-semibold">Edit</a>
                                    <form action="/delete/{{ contact.id }}" method="post" class="inline-block" onsubmit="return confirm('Are you sure you want to delete this contact?');">
                                        <button type="submit" class="text-red-600 hover:text-red-900 font-semibold bg-transparent border-none cursor-pointer p-0">Delete</button>
                                    </form>
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <p class="text-center text-gray-600 text-lg">No contacts found in the database.</p>
        {% endif %}
    </div>
</body>
</html>
"""

# HTML template for editing a contact
EDIT_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Contact</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
    </style>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen p-4">
    <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
        <h1 class="text-3xl font-bold text-gray-800 mb-6 text-center">Edit Contact</h1>

        {% if contact %}
            <form action="/edit/{{ contact.id }}" method="post" class="space-y-4">
                <input type="hidden" name="id" value="{{ contact.id }}">
                <div>
                    <label for="name" class="block text-sm font-medium text-gray-700">Name</label>
                    <input type="text" id="name" name="name" value="{{ contact.name }}" required
                           class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                </div>
                <div>
                    <label for="phone" class="block text-sm font-medium text-gray-700">Phone</label>
                    <input type="text" id="phone" name="phone" value="{{ contact.phone }}"
                           class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                </div>
                <div>
                    <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
                    <input type="email" id="email" name="email" value="{{ contact.email }}"
                           class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                </div>
                <div class="flex justify-end space-x-3">
                    <a href="/" class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                        Cancel
                    </a>
                    <button type="submit" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                        Update Contact
                    </button>
                </div>
            </form>
        {% else %}
            <p class="text-center text-red-600 text-lg">Contact not found.</p>
        {% endif %}
    </div>
</body>
</html>
"""

conn_str = "DRIVER={ODBC Driver 17 for SQL Server};"
conn_str += f"SERVER={server_name};"
conn_str += f"DATABASE={database_name};"
conn_str += f"UID={database_username};"
conn_str += f"PWD={database_password};"


def get_contacts_from_db_pyodbc():
    """
    Connects to a database using pyodbc,
    and retrieves and prints all records from the 'contacts' table.
    """
    conn = None # Initialize connection to None
    try:
        # IMPORTANT: Replace with your actual connection string.
        # Examples:
        # For SQL Server:
        conn_str = "DRIVER={ODBC Driver 17 for SQL Server};"
        conn_str += f"SERVER={server_name};"
        conn_str += f"DATABASE={database_name};"
        conn_str += f"UID={database_username};"
        conn_str += f"PWD={database_password};"

        print(f"Attempting to connect to database using connection string: {conn_str}\n")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # --- For demonstration, let's assume the 'contacts' table already exists. ---
        # In a real application, you might have DDL (Data Definition Language)
        # to create tables, but pyodbc is typically used with existing databases.
        # Example of creating a table (uncomment if needed for testing, adjust for your DB syntax):
        # try:
        #     cursor.execute('''
        #         CREATE TABLE contacts (
        #             id INT PRIMARY KEY IDENTITY(1,1), -- For SQL Server
        #             name NVARCHAR(255) NOT NULL,
        #             phone NVARCHAR(50),
        #             email NVARCHAR(255)
        #         )
        #     ''')
        #     conn.commit()
        #     print("Contacts table created (if it didn't exist).")
        # except pyodbc.ProgrammingError as e:
        #     if "already exists" in str(e): # Check for table already exists error
        #         print("Contacts table already exists.")
        #     else:
        #         raise e # Re-raise other programming errors

        # --- Insert sample data if the table is empty (optional, adjust for your DB syntax) ---
        # This part is highly dependent on your database's SQL dialect.
        # For SQL Server, you might check if records exist and then insert.
        try:
            cursor.execute("SELECT COUNT(*) FROM contacts")
            if cursor.fetchone()[0] == 0:
                print("Inserting sample data...")
                cursor.execute("INSERT INTO contacts (id, name, phone, email, active) VALUES (?, ?, ?, ?, ?)", (10, 'Alice Smith', '123-456-7890', 'alice@example.com', True))
                cursor.execute("INSERT INTO contacts (id, name, phone, email,active) VALUES (?, ?, ?, ?, ?)", (15, 'Bob Johnson', '098-765-4321', 'bob@example.com', True))
                cursor.execute("INSERT INTO contacts (id, name, phone, email,active) VALUES (?, ?, ?, ?, ?)", (17, 'Charlie Brown', '555-123-4567', 'charlie@example.com', False))
                conn.commit()
                print("Sample data inserted.")
            else:
                print("Contacts table already contains data.")
        except pyodbc.ProgrammingError as e:
            print(f"Could not check/insert sample data (table might not exist or syntax error): {e}")
            # Continue to attempt fetching, as the table might exist with data already.


        # Select all records from the 'contacts' table
        print("\nRetrieving records from the 'contacts' table:")
        cursor.execute("SELECT id, name, phone, email FROM contacts")
        records = cursor.fetchall()

        if records:
            for row in records:
                # Access columns by index or by name if you fetch column names
                print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}, Email: {row[3]}")
        else:
            print("No records found in the 'contacts' table.")

    except pyodbc.Error as e:
        sqlstate = e.args[0]
        # Example error handling for common issues
        if sqlstate == '28000':
            print(f"Authentication error: Check username/password or DSN configuration. Error: {e}")
        elif sqlstate == '08001':
            print(f"Connection error: Server not found or inaccessible. Error: {e}")
        else:
            print(f"A pyodbc error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the database connection is closed even if an error occurs
        if conn:
            conn.close()
            print("\nDatabase connection closed.")


def fetch_contacts_data(conn_str):
    """
    Connects to a database using pyodbc,
    and retrieves all records from the 'contacts' table.
    Returns a list of dictionaries, where each dictionary represents a contact.
    """
    conn = None # Initialize connection to None
    contacts = []
    try:
        # IMPORTANT: Replace with your actual connection string.
        # Examples:
        # For SQL Server:
        # conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=your_server_name;DATABASE=test;UID=your_username;PWD=your_password"
        # For a DSN (Data Source Name) configured on your system:
        # conn_str = "DSN=your_dsn_name"
        # For a local SQLite database (using pyodbc's SQLite driver, if available, or via a DSN)
        # Note: For SQLite, it's often simpler to use the built-in `sqlite3` module directly,
        # but this example adheres to the `pyodbc` requirement.
        # conn_str = "DRIVER={SQLite3 ODBC Driver};Database=test.db" # Example for SQLite with pyodbc

        print(f"Attempting to connect to database using connection string: {conn_str}")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # --- Create table if it doesn't exist and insert sample data ---
        # This part is highly dependent on your database's SQL dialect.
        # For demonstration, using SQLite-compatible syntax for table creation.
        try:
            # Check if table exists (this approach is common but might vary by DB)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contacts';")
            table_exists = cursor.fetchone()

            if not table_exists:
                print("Creating 'contacts' table...")
                cursor.execute('''
                    CREATE TABLE contacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone TEXT,
                        email TEXT
                    )
                ''')
                conn.commit()
                print("Contacts table created.")

            # Insert sample data if the table is empty
            cursor.execute("SELECT COUNT(*) FROM contacts")
            if cursor.fetchone()[0] == 0:
                print("Inserting sample data...")
                cursor.execute("INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)", ('Alice Smith', '123-456-7890', 'alice@example.com'))
                cursor.execute("INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)", ('Bob Johnson', '098-765-4321', 'bob@example.com'))
                cursor.execute("INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)", ('Charlie Brown', '555-123-4567', 'charlie@example.com'))
                conn.commit()
                print("Sample data inserted.")
            else:
                print("Contacts table already contains data.")

        except pyodbc.ProgrammingError as e:
            print(f"Could not check/create/insert sample data (table might exist or syntax error): {e}")
            # Continue to attempt fetching, as the table might exist with data already.


        # Select all records from the 'contacts' table
        print("\nRetrieving records from the 'contacts' table for web display:")
        cursor.execute("SELECT id, name, phone, email FROM contacts")
        
        # Fetch column names from the cursor description
        columns = [column[0] for column in cursor.description]
        
        for row in cursor.fetchall():
            # Create a dictionary for each row using column names
            contact = dict(zip(columns, row))
            contacts.append(contact)

    except pyodbc.Error as e:
        sqlstate = e.args[0]
        if sqlstate == '28000':
            print(f"Authentication error: Check username/password or DSN configuration. Error: {e}")
        elif sqlstate == '08001':
            print(f"Connection error: Server not found or inaccessible. Error: {e}")
        else:
            print(f"A pyodbc error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")
    return contacts

def get_single_contact(contact_id, CONN_STR):
    """
    Fetches a single contact record from the database by ID.
    Returns a dictionary representing the contact, or None if not found.
    """
    conn = None
    contact = None
    try:
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone, email FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            contact = dict(zip(columns, row))
    except pyodbc.Error as e:
        print(f"Error fetching single contact: {e}")
    finally:
        if conn:
            conn.close()
    return contact

def update_contact_data(contact_id, name, phone, email,CONN_STR):
    """
    Updates an existing contact record in the database.
    """
    conn = None
    try:
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        cursor.execute("UPDATE contacts SET name = ?, phone = ?, email = ? WHERE id = ?",
                       (name, phone, email, contact_id))
        conn.commit()
        print(f"Contact with ID {contact_id} updated successfully.")
    except pyodbc.Error as e:
        print(f"Error updating contact: {e}")
    finally:
        if conn:
            conn.close()

@app.route("/")
def list_contacts():
    """
    Flask route to list all contacts from the database.
    """
    contacts = fetch_contacts_data(conn_str)
    return render_template_string(HTML_TEMPLATE, contacts=contacts)

@app.route("/edit/<int:contact_id>", methods=['GET', 'POST'])
def edit_contact(contact_id):
    """
    Flask route for editing a contact.
    GET: Displays the edit form pre-filled with contact data.
    POST: Processes the form submission and updates the contact in the database.
    """
    if request.method == 'POST':
        # Handle form submission to update contact
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        
        update_contact_data(contact_id, name, phone, email, conn_str)
        return redirect(url_for('list_contacts'))
    else:
        # Handle GET request to display the edit form
        contact = get_single_contact(contact_id, conn_str)
        if contact:
            return render_template_string(EDIT_HTML_TEMPLATE, contact=contact)
        else:
            return render_template_string(EDIT_HTML_TEMPLATE, contact=None) # Or a proper error page

@app.route("/delete/<int:contact_id>", methods=['POST'])
def delete_contact(contact_id):
    """
    Placeholder Flask route for deleting a contact.
    In a real application, this would delete the contact from the database.
    """
    # In a real application, you would add database deletion logic here.
    # For example:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()
    conn.close()
    print(f"Attempting to delete contact with ID: {contact_id} (Functionality to be implemented)")
    return redirect(url_for('list_contacts')) # Redirect back to the contact list after "deletion"

if __name__ == "__main__":
    # You need to install Flask: pip install Flask
    # You need to install pyodbc: pip install pyodbc
    # You also need an ODBC driver for your specific database (e.g., SQL Server ODBC Driver, SQLite3 ODBC Driver)
    app.run(debug=True) # debug=True allows for automatic reloading and provides a debugger
    
    
    
# Call the function to execute the database operations
# if __name__ == "__main__":
#     # You need to install pyodbc: pip install pyodbc
#     # You also need an ODBC driver for your specific database (e.g., SQL Server ODBC Driver)
#     get_contacts_from_db_pyodbc()
