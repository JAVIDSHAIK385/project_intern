import psycopg2
from psycopg2 import extras

# ------------------ DATABASE CONNECTION ------------------
def connect_db():
    return psycopg2.connect(
        dbname="bank_db",
        user="postgres",
        password="12@24@08",
        host="localhost",
        port="5432"
    )

# ------------------ ACCOUNT CREATION ------------------
def create_user(username, password, initial_balance):
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING user_id",
            (username, password)
        )
        user_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO accounts (user_id, balance) VALUES (%s, %s)",
            (user_id, initial_balance)
        )
        conn.commit()
        print(f"✅ Account created successfully for {username}")
    except Exception as e:
        conn.rollback()
        print("❌ Error creating user:", e)
    finally:
        cur.close()
        conn.close()

# ------------------ USER LOGIN ------------------
def login(username, password):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id FROM users WHERE TRIM(username)=%s AND TRIM(password)=%s",
        (username.strip(), password.strip())
    )
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        print("✅ Login successful!")
        return user[0]
    else:
        print("❌ Invalid credentials")
        return None

# ------------------ GET ACCOUNT ID ------------------
def get_account_id(user_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT account_id FROM accounts WHERE user_id=%s", (user_id,))
    account = cur.fetchone()
    cur.close()
    conn.close()
    return account[0] if account else None

# ------------------ TRANSFER FUNDS ------------------
def transfer_funds(sender_acc, receiver_acc, amount):
    conn = connect_db()
    cur = conn.cursor()
    try:
        conn.autocommit = False  # Start transaction

        # Check balances
        cur.execute("SELECT balance FROM accounts WHERE account_id=%s", (sender_acc,))
        sender_balance = cur.fetchone()[0]

        if sender_balance < amount:
            raise Exception("Insufficient funds")

        # Deduct from sender
        cur.execute("UPDATE accounts SET balance = balance - %s WHERE account_id=%s", (amount, sender_acc))

        # Add to receiver
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE account_id=%s", (amount, receiver_acc))

        # Record transaction
        cur.execute("INSERT INTO transactions (sender_id, receiver_id, amount) VALUES (%s, %s, %s)",
                    (sender_acc, receiver_acc, amount))

        conn.commit()
        print(f"💸 Transfer of ₹{amount} successful!")
    except Exception as e:
        conn.rollback()
        print("❌ Transaction failed:", e)
    finally:
        cur.close()
        conn.close()

# ------------------ VIEW TRANSACTION HISTORY ------------------
def view_transactions(account_id):
    conn = connect_db()
    cur = conn.cursor(cursor_factory=extras.DictCursor)
    cur.execute("""
        SELECT trans_id, sender_id, receiver_id, amount, trans_date 
        FROM transactions
        WHERE sender_id = %s OR receiver_id = %s
        ORDER BY trans_date DESC
    """, (account_id, account_id))
    records = cur.fetchall()
    cur.close()
    conn.close()

    print("\n📜 Transaction History:")
    for r in records:
        print(f"ID: {r['trans_id']}, From: {r['sender_id']} → To: {r['receiver_id']}, Amount: ₹{r['amount']}, Date: {r['trans_date']}")

# ------------------ MAIN SIMULATION ------------------
if __name__ == "__main__":
    print("🏦 Simple Banking System\n")

    # Step 1: Create users (run only once)
    create_user("javid", "1234", 5000)
    create_user("arun", "5678", 2000)

    # Step 2: Login
    uid = login("javid", "1234")
    if uid:
        acc_id = get_account_id(uid)

        # Step 3: Transfer funds
        receiver_acc = 2  # arun's account
        transfer_funds(acc_id, receiver_acc, 1000)

        # Step 4: View transactions
        view_transactions(acc_id)
