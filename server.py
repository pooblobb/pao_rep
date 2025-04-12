import socket
import random
import json


difficulty = 'a'
last_difficulty = 'a'
host = '127.0.0.1'
port = 12345
banner = """
🎮 Welcome to the Number Guessing Game! 🎮

Please select your mode:
👤 Manual - Play the game yourself
🤖 Bot - Let an AI guess optimally
Type 'manual' or 'bot' to begin: """

def generate_random_int(difficulty):
    if difficulty == 'a':
        return random.randint(1, 50)
    elif difficulty == 'b':
        return random.randint(1, 100)
    elif difficulty == 'c':
        return random.randint(1, 500)

def update_leaderboard(name, score, difficulty, leaderboard):
    leaderboard.append({"name": name, "score": score, "difficulty": difficulty})
    leaderboard.sort(key=lambda x: x["score"])
    return leaderboard[:10]

def save_leaderboard(leaderboard):
    with open("leaderboard.json", "w") as f:
        json.dump(leaderboard, f)

def load_leaderboard():
    try:
        with open("leaderboard.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def filter_leaderboard_by_difficulty(leaderboard, difficulty):
    return [entry for entry in leaderboard if entry["difficulty"] == difficulty]

def format_leaderboard(leaderboard):
    formatted = "🏆 Top Players 🏆\n"
    for i, entry in enumerate(leaderboard, 1):
        formatted += f"{i}. Player: {entry['name']}, Attempts: {entry['score']}\n"
    return formatted

PASSWORD = "Joshua"

def authenticate(conn):
    conn.sendall("🔒 Please enter the password to play: ".encode('utf-8'))
    
    while True:
        entered_password = conn.recv(1024).decode('utf-8').strip()
        
        if not entered_password:  # Ensure the client has entered something
            conn.sendall("⚠ Please enter a valid password: ".encode('utf-8'))
            continue  # Keep asking for input
        
        if entered_password == PASSWORD:
            conn.sendall("✅ Access granted! Let's play!\n".encode('utf-8'))
            return True
        else:
            conn.sendall("❌ Incorrect password. Connection closing...\n".encode('utf-8'))
            conn.close()
            return False

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)

    print(f"🚀 Server is running on {host}:{port}")
    guessme = 0
    conn = None
    leaderboard = load_leaderboard()


    while True:
        client_input = str(input("Please Select from a,b,c."))
        if conn is None:
            print("Waiting for connection...")
            conn, addr = s.accept()
            print(f"New client connected: {addr[0]}")
            if not authenticate(conn):
                continue  

            conn.sendall(banner.encode('utf-8'))
            mode = conn.recv(1024).decode().strip()

            if mode == "bot":
                bot_guessing_game(conn)
            elif mode == "manual":
                manual_guessing_game(conn)
            else:
                conn.sendall("❌ Invalid choice! Please enter 'manual' or 'bot'.".encode('utf-8'))
                conn.close()
                conn.sendall(banner.encode('utf-8'))
            if client_input in ['a', 'b', 'c']:
                difficulty = client_input
                last_difficulty = difficulty
                guessme = generate_random_int(difficulty)
                conn.sendall("\n".encode('utf-8'))
                tries = 0
            elif client_input.isdigit():
                guess = int(client_input)
                print(f"User guess attempt: {guess}")
                tries += 1
                if guess == guessme:
                    print(f"Tries count: {tries}")
                    if tries >= 1 and tries <= 5:  
                        print("Sending: Excellent")
                        conn.sendall("Excellent".encode('utf-8'))
                    elif tries >= 6 and tries <= 20:  
                        print("Sending: Very Good")
                        conn.sendall("✔ Very Good".encode('utf-8'))
                    elif tries >= 21:
                        print("Sending: Good/Fair") 
                        conn.sendall("Good/Fair".encode('utf-8'))
                    print("Sending congratulations message!")  
                    conn.sendall("🎉 Congratulations! You got it right!\nPlease enter your name: ".encode('utf-8'))
                    
                    name = conn.recv(1024).decode('utf-8').strip()
                    score = tries
                    update_leaderboard(name, score, difficulty, leaderboard)
                    save_leaderboard(leaderboard)
                    conn.sendall("\n".encode('utf-8'))
                    try_again = conn.recv(1024).decode('utf-8').strip()
                    if try_again == 'y':
                        conn.sendall("Continuing".encode('utf-8'))
                    elif try_again == 'n':
                        conn.sendall("\nLeaderboard:\n" + format_leaderboard(filter_leaderboard_by_difficulty(leaderboard, difficulty)).encode('utf-8'))
                        conn.close()
                        print("Connection closed.")
                    else:
                        conn.sendall("Invalid input!".encode('utf-8'))
                elif guess > guessme:
                    conn.sendall("📉 Too high! Try a lower number: ".encode('utf-8'))
                    continue
                elif guess < guessme:
                    conn.sendall("📈 Too low! Try a higher number: ".encode('utf-8'))
                    continue
            elif client_input == "":
                print("❌ Empty Input received.")
            else:
                conn.sendall("❌ Invalid input!\nPlease enter a number or choose difficulty (a/b/c): ".encode('utf-8'))
                
def bot_guessing_game(conn):
    """ The bot plays using binary search. """
    conn.sendall("🎮 Choose difficulty (a/b/c): ".encode('utf-8'))
    difficulty = conn.recv(1024).decode().strip()
    
    low, high = 1, 50 if difficulty == 'a' else 100 if difficulty == 'b' else 500
    guessme = random.randint(low, high)  # Random target number
    tries = 0

    conn.sendall("🤖 Bot is playing...\n".encode('utf-8'))

    while True:
        bot_guess = (low + high) // 2  # Binary search optimization
        tries += 1
        conn.sendall(f"🤖 Bot guesses: {bot_guess}\n".encode('utf-8'))

        if bot_guess == guessme:
            conn.sendall(f"🏆 Bot won in {tries} attempts!\n".encode('utf-8'))
            break
        elif bot_guess > guessme:
            high = bot_guess - 1
            conn.sendall("📉 Too high! Adjusting...\n".encode('utf-8'))
        elif bot_guess < guessme:
            low = bot_guess + 1
            conn.sendall("📈 Too low! Adjusting...\n".encode('utf-8'))

    conn.close()


def manual_guessing_game(conn):
    """ Standard guessing game for human players. """
    conn.sendall("🎮 Choose difficulty (a/b/c): ".encode('utf-8'))
    difficulty = conn.recv(1024).decode().strip()
    guessme = generate_random_int(difficulty)
    tries = 0
    conn.sendall("🎯 Enter your guess: ".encode('utf-8'))

    while True:
        client_input = conn.recv(1024).decode().strip()

        if client_input.isdigit():
            guess = int(client_input)
            tries += 1

            if guess == guessme:
                conn.sendall(f"🎉 You won in {tries} attempts!\n".encode('utf-8'))
                break
            elif guess > guessme:
                conn.sendall("📉 Too high! Try a lower number: ".encode('utf-8'))
            elif guess < guessme:
                conn.sendall("📈 Too low! Try a higher number: ".encode('utf-8'))
        else:
            conn.sendall("❌ Invalid input! Enter a number: ".encode('utf-8'))

    conn.close()

def server():
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
    if WindowsError:
        print("Windows Error.")



if __name__ == "__main__":
    server()