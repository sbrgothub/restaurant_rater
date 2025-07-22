# database/create_database.py (NEW VERSION)
import sqlite3

# IMPORTANT: You must delete your old 'feedback.db' file before running this script
# for the changes to take effect.

conn = sqlite3.connect('feedback.db')
cursor = conn.cursor()

# 1. Create 'foods' table with new columns
print("Creating 'foods' table with total_quantity and rating_count...")
cursor.execute("DROP TABLE IF EXISTS foods") # Drop old table to ensure schema update
cursor.execute('''
CREATE TABLE foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    total_stars INTEGER DEFAULT 0,
    total_quantity INTEGER DEFAULT 0, -- RENAMED and will be updated by cashier app
    rating_count INTEGER DEFAULT 0    -- NEW column, updated when a user rates
)
''')

# --- The other tables remain the same ---
# 2. Create 'transactions' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unique_id TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT 'NEW',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
# 3. Create 'transaction_items' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS transaction_items (
    transaction_id INTEGER,
    food_name TEXT NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions (id)
)
''')
# 4. Create 'service_ratings' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS service_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comfort_rating INTEGER NOT NULL,
    service_rating INTEGER NOT NULL,
    staff_rating INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()
print("Database 'feedback.db' created successfully with the new schema.")