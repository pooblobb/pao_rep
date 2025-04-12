import socket

HOST = "127.0.0.1"
PORT = 12345
def bot_play(s):
    """ The bot plays the guessing game optimally. """
    print("🤖 Bot is playing...")

    # Bot starts with a reasonable range
    low, high = 1, 500  # Adjust based on difficulty selection
    bot_guess = (low + high) // 2  # Initial guess (middle of the range)

    while True:
        print(f"🤖 Bot guesses: {bot_guess}")
        s.sendall(str(bot_guess).encode())

        response = s.recv(1024).decode()
        print(response)

        if "Congratulations" in response:
            break  # Bot won!

        elif "Too high" in response:
            high = bot_guess - 1  # Reduce upper bound
        elif "Too low" in response:
            low = bot_guess + 1  # Increase lower bound
        
        bot_guess = (low + high) // 2  # New guess (binary search)
    
    print("🏆 Bot has won the game!")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print("🎮 Connected to the game server!")

            password_prompt = s.recv(1024).decode()
            print(password_prompt)
            user_password = input("🔒 Enter password: ")
            s.sendall(user_password.encode())

            auth_response = s.recv(1024).decode()
            print(auth_response)

            if "Incorrect password" in auth_response:
                return  

            banner = s.recv(1024).decode()
            print(banner)

            mode_choice = input("👤 Play manually or let 🤖 Bot play? (manual/bot): ").strip().lower()
            s.sendall(mode_choice.encode())

            if mode_choice == "bot":
                difficulty_prompt = s.recv(1024).decode()
                print(difficulty_prompt)
                difficulty_choice = input("Choose difficulty level (a/b/c): ")
                s.sendall(difficulty_choice.encode())

                bot_play(s)  # Bot takes over after difficulty selection
            else:
                print("⚠ Invalid choice! Type 'manual' or 'bot'.")
                
        except Exception as e:
            print(f"❌ An error occurred: {e}")

def client():
    try:
        main()
    except ConnectionRefusedError:
        print("❌ Unable to connect to the server. Please make sure the server is running.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        print("👋 Thanks for playing! See you next time!")

if __name__ == "__main__":
    client()