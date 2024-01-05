import sqlite3

def create_database():
    # Create a SQLite database to store user credits
    conn = sqlite3.connect('user_credits.db')
    cursor = conn.cursor()

    # Create table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            free_credits INTEGER,
            earned_credits INTEGER
        )
    ''')
    conn.commit() 
    conn.close()

def add_user(user_id):
    # Add a new user to the database with initial credits
    conn = sqlite3.connect('user_credits.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO users (user_id, free_credits, earned_credits) 
        VALUES (?, 2, 0)
    ''', (user_id,))
    conn.commit()
    conn.close()

def get_user_credits(user_id):
    # Get the sum of user credits
    conn = sqlite3.connect('user_credits.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT (free_credits + earned_credits) as total_credits 
        FROM users WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        # If user is not found, add them and return initial credits
        add_user(user_id)
        return 2

def update_user_credits(user_id, credits_to_add):
    # Adds credits to the "earned credit" section
    conn = sqlite3.connect('user_credits.db')
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    if not cursor.fetchone():
        # If user does not exist, add them
        add_user(user_id)

    cursor.execute('''
        UPDATE users SET earned_credits = earned_credits + ? 
        WHERE user_id = ?
    ''', (credits_to_add, user_id))
    conn.commit()
    conn.close()

def use_credit(user_id):
    # Checks if user has free credits
    conn = sqlite3.connect('user_credits.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT free_credits FROM users WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        free_credits = result[0]
        if free_credits > 0:
            # If user has free credits, decrement them
            conn = sqlite3.connect('user_credits.db')
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE users SET free_credits = free_credits - 1 
                WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
            conn.close()
            return True

    conn = sqlite3.connect('user_credits.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT earned_credits FROM users WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        earned_credits = result[0]
        if earned_credits > 0:
            # If user has earned credits, decrement them
            conn = sqlite3.connect('user_credits.db')
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE users SET earned_credits = earned_credits - 1 
                WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
            conn.close()
            return True
        
    return False


def refresh_free_credits():
    # Sets the free credits back to two for all users
    conn = sqlite3.connect('user_credits.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE users SET free_credits = 2
    ''')
    conn.commit()
    conn.close()


