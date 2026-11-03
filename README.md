🎮 NEON ARCADE
🏎️ Multiplayer Gaming Platform

Two games. Two players. One local network. Endless fun.

Neon Arcade is a multiplayer gaming platform built with Python, Flask and Socket.IO. It features two different multiplayer games that you can play with your friends over a local network.

✨ Features
🌐 Real-time multiplayer over LAN
🎮 Interactive game selection menu
⚡ Cyber Arena – cyber-themed multiplayer game
🏎️ Neon Rush 2.0 – futuristic multiplayer racing
🏁 Three-lap racing system
🏆 Race results and rematches
🎨 Neon-inspired user interface
⚙️ Simple installation and setup
🎮 Available Games
⚡ Cyber Arena

A cyber-themed multiplayer experience where players compete in an interactive arena.

🏎️ Neon Rush 2.0

A futuristic racing game where two players compete to become the ultimate champion.

Features:

Real-time multiplayer
Two-player racing
Three laps per race
Live player positions
Race results
Rematch system
Neon racing interface
🖥️ Screenshots

Screenshots coming soon!

🚀 Installation & Setup

Follow this tutorial to download and run Neon Arcade on your computer.

📋 Requirements

Before starting, make sure you have:

Python 3.10 or newer
Git
pip
Internet connection for installation
A local network connection for multiplayer
1️⃣ Download the project

Open your terminal and clone the repository:

bash
git clone https://github.com/YOUR-USERNAME/neon-arcade.git


Enter the project directory:

bash
cd neon-arcade

2️⃣ Install required packages

On Ubuntu or Debian, install Python and the required tools:

bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git

3️⃣ Create a virtual environment
bash
python3 -m venv .venv


Activate it:

bash
source .venv/bin/activate

4️⃣ Install dependencies
bash
pip install -r requirements.txt

5️⃣ Start Neon Arcade

Run the application:

bash
python app.py


🎉 Congratulations! Neon Arcade is now running.

🌐 Multiplayer – Connect with Friends

Neon Arcade is designed to work over a local network.

Step 1 – Find your server IP

On the computer running the server, execute:

bash
hostname -I


Example output:

text
192.168.10.40

Step 2 – Open the game

On the server computer, open:

text
http://localhost:5000


On another computer connected to the same network, open:

text
http://192.168.10.40:5000


Replace the IP address with your actual server IP.

Step 3 – Start playing
Open Neon Arcade.
Choose your preferred game.
Invite another player.
Connect to the same server.
Enjoy multiplayer gaming!
Note: Make sure both computers can communicate over the local network. Allow incoming TCP connections on port 5000 in your firewall if necessary.
🏎️ Neon Rush Controls
Action	Keyboard
Accelerate	W / ↑
Brake	S / ↓
Turn left	A / ←
Turn right	D / →
Drift	SPACE
🔄 Restarting the Server

To stop the application:

bash
CTRL + C


To start it again:

bash
cd neon-arcade
source .venv/bin/activate
python app.py

🛠️ Troubleshooting
❌ Python virtual environment is unavailable

Install the required package:

bash
sudo apt install python3-venv

❌ Cannot connect to the server

Check the following:

Both computers are connected to the same network.
You are using the correct server IP.
The server is running.
TCP port 5000 is allowed through the firewall.
❌ Missing Python dependencies

Activate your virtual environment and reinstall:

bash
source .venv/bin/activate
pip install -r requirements.txt

❌ Port 5000 is already in use

Check which process is using the port:

bash
sudo ss -ltnp | grep 5000

🧰 Technologies
Technology	Purpose
Python	Backend
Flask	Web server
Flask-SocketIO	Multiplayer communication
Socket.IO	Real-time communication
HTML5	Game structure
CSS3	Visual design
JavaScript	Game logic
Canvas	Game rendering
📁 Project Structure
text
neon-arcade/
│
├── app.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── index.html
│   ├── arena.html
│   └── race.html
│
└── static/
    ├── css/
    ├── js/
    └── images/


The actual structure may vary depending on the project version.

🗺️ Future Plans

Potential future improvements:

More multiplayer games
Additional racing tracks
Car customization
Player statistics and records
Improved racing physics
Sound effects and music
Improved mobile support
Online multiplayer support
👨‍💻 Project Information

Project: Neon Arcade
Version: 2.0
Platform: Linux / Windows
Game mode: Local multiplayer
Players: Designed for two players

❤️ Enjoy the game!

If you like the project, consider giving it a ⭐ on GitHub!

NEON ARCADE — PLAY TOGETHER. COMPETE TOGETHER. 🚀
