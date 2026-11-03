import math
import random
import time
from threading import RLock

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "cyber-arena-2"
socketio = SocketIO(app, async_mode="threading", cors_allowed_origins="*")

W, H = 1200, 750
lock = RLock()
players = {}
bullets = []
pickups = []
effects = []
last_pickup = 0

COLORS = ["#00f5ff", "#ff3d78", "#b56cff", "#ffe45c"]

WEAPONS = {
    "laser": {"damage": 25, "speed": 850, "rate": .20, "count": 1},
    "shotgun": {"damage": 13, "speed": 620, "rate": .85, "count": 6},
    "rapid": {"damage": 9, "speed": 760, "rate": .075, "count": 1},
}

WALLS = [
    {"x": 220, "y": 130, "w": 110, "h": 110},
    {"x": 870, "y": 130, "w": 110, "h": 110},
    {"x": 220, "y": 510, "w": 110, "h": 110},
    {"x": 870, "y": 510, "w": 110, "h": 110},
    {"x": 510, "y": 250, "w": 180, "h": 75},
    {"x": 510, "y": 425, "w": 180, "h": 75},
]

def spawn_position():
    for _ in range(100):
        x, y = random.randint(65, W-65), random.randint(65, H-65)
        if not blocked(x, y):
            return x, y
    return W/2, H/2

def blocked(x, y):
    if x < 22 or x > W-22 or y < 22 or y > H-22:
        return True
    for wall in WALLS:
        if (wall["x"]-20 < x < wall["x"]+wall["w"]+20
                and wall["y"]-20 < y < wall["y"]+wall["h"]+20):
            return True
    return False

def create_player(sid, name):
    x, y = spawn_position()
    return {
        "id": sid, "name": name, "x": x, "y": y,
        "color": COLORS[len(players) % len(COLORS)],
        "hp": 100, "shield": 0,
        "score": 0, "kills": 0, "deaths": 0,
        "angle": 0, "weapon": "laser",
        "input": {}, "cooldown": 0, "dash": 0,
        "dash_cooldown": 0, "speed_boost": 0,
        "respawn": 0
    }

@app.route("/")
def index():
    return render_template("menu.html")

@app.route("/arena")
def arena():
    return render_template("arena.html")

@app.route("/race")
def race():
    return render_template("race.html")

@socketio.on("join")
def join(data):
    sid = request.sid
    name = str(data.get("name", "Player")).strip()[:16] or "Player"
    with lock:
        if sid not in players:
            players[sid] = create_player(sid, name)
    emit("joined", {"id": sid})

@socketio.on("input")
def player_input(data):
    with lock:
        p = players.get(request.sid)
        if p:
            p["input"] = {
                "w": bool(data.get("w")),
                "a": bool(data.get("a")),
                "s": bool(data.get("s")),
                "d": bool(data.get("d")),
                "fire": bool(data.get("fire")),
                "dash": bool(data.get("dash")),
                "angle": max(-math.pi, min(math.pi, float(data.get("angle", 0)))),
                "weapon": str(data.get("weapon", "laser"))
            }

@socketio.on("disconnect")
def disconnect():
    with lock:
        players.pop(request.sid, None)
        if request.sid in race_players:
            race_players.pop(request.sid, None)
        bullets[:] = [b for b in bullets if b["owner"] != request.sid]

def damage_player(p, damage):
    absorbed = min(p["shield"], damage)
    p["shield"] -= absorbed
    p["hp"] -= damage - absorbed

def spawn_pickup():
    x, y = spawn_position()
    kind = random.choice(["health", "shield", "speed"])
    pickups.append({"x": x, "y": y, "kind": kind, "life": 15})

def game_loop():
    global last_pickup
    previous = time.monotonic()

    while True:
        now = time.monotonic()
        dt = min(now-previous, .04)
        previous = now

        with lock:
            for sid, p in list(players.items()):
                if p["respawn"] > 0:
                    p["respawn"] -= dt
                    if p["respawn"] <= 0:
                        p["x"], p["y"] = spawn_position()
                        p["hp"] = 100
                        p["shield"] = 0
                    continue

                c = p["input"]
                p["cooldown"] = max(0, p["cooldown"]-dt)
                p["dash_cooldown"] = max(0, p["dash_cooldown"]-dt)
                p["speed_boost"] = max(0, p["speed_boost"]-dt)
                p["angle"] = c.get("angle", 0)

                dx = int(c.get("d", False))-int(c.get("a", False))
                dy = int(c.get("s", False))-int(c.get("w", False))
                length = math.hypot(dx, dy)

                if length:
                    dx, dy = dx/length, dy/length

                if c.get("dash") and p["dash_cooldown"] <= 0 and length:
                    p["dash"] = .13
                    p["dash_cooldown"] = 2.2

                if p["dash"] > 0:
                    p["dash"] -= dt
                    speed = 950
                else:
                    speed = 270 if not p["speed_boost"] else 390

                nx = p["x"] + dx*speed*dt
                ny = p["y"] + dy*speed*dt

                if not blocked(nx, p["y"]):
                    p["x"] = nx
                if not blocked(p["x"], ny):
                    p["y"] = ny

                weapon = c.get("weapon", "laser")
                if weapon not in WEAPONS:
                    weapon = "laser"

                if c.get("fire") and p["cooldown"] <= 0:
                    spec = WEAPONS[weapon]
                    for i in range(spec["count"]):
                        spread = (i-(spec["count"]-1)/2)*.105
                        angle = p["angle"]+spread
                        bullets.append({
                            "x": p["x"]+math.cos(angle)*24,
                            "y": p["y"]+math.sin(angle)*24,
                            "vx": math.cos(angle)*spec["speed"],
                            "vy": math.sin(angle)*spec["speed"],
                            "owner": sid,
                            "damage": spec["damage"],
                            "life": 1.3,
                            "color": p["color"]
                        })
                    p["cooldown"] = spec["rate"]

            for b in bullets[:]:
                b["x"] += b["vx"]*dt
                b["y"] += b["vy"]*dt
                b["life"] -= dt
                remove = b["life"] <= 0 or blocked(b["x"], b["y"])

                if not remove:
                    for sid, p in players.items():
                        if sid == b["owner"] or p["respawn"] > 0:
                            continue
                        if math.hypot(p["x"]-b["x"], p["y"]-b["y"]) < 23:
                            damage_player(p, b["damage"])
                            remove = True
                            effects.append({
                                "x": b["x"], "y": b["y"],
                                "life": .25, "color": b["color"]
                            })

                            if p["hp"] <= 0:
                                p["deaths"] += 1
                                p["respawn"] = 2.5
                                killer = players.get(b["owner"])
                                if killer:
                                    killer["kills"] += 1
                                    killer["score"] += 1
                                socketio.emit("notice", {
                                    "text": p["name"]+" byl vyřazen!"
                                })
                            break

                if remove and b in bullets:
                    bullets.remove(b)

            for pickup in pickups[:]:
                pickup["life"] -= dt
                if pickup["life"] <= 0:
                    pickups.remove(pickup)
                    continue

                for p in players.values():
                    if p["respawn"] > 0:
                        continue
                    if math.hypot(p["x"]-pickup["x"], p["y"]-pickup["y"]) < 28:
                        if pickup["kind"] == "health":
                            p["hp"] = min(100, p["hp"]+40)
                        elif pickup["kind"] == "shield":
                            p["shield"] = min(100, p["shield"]+50)
                        else:
                            p["speed_boost"] = 8
                        socketio.emit("notice", {
                            "text": p["name"]+" získal bonus!"
                        })
                        pickups.remove(pickup)
                        break

            if now-last_pickup > 9 and len(pickups) < 4:
                spawn_pickup()
                last_pickup = now

            for e in effects[:]:
                e["life"] -= dt
                if e["life"] <= 0:
                    effects.remove(e)

            state = {
                "players": [
                    {k: p[k] for k in (
                        "id", "name", "x", "y", "color", "hp",
                        "shield", "score", "kills", "deaths",
                        "angle", "weapon", "respawn",
                        "dash_cooldown", "speed_boost"
                    )}
                    for p in players.values()
                ],
                "bullets": [
                    {k: b[k] for k in ("x", "y", "color")}
                    for b in bullets
                ],
                "pickups": [
                    {k: v[k] for k in ("x", "y", "kind")}
                    for v in pickups
                ],
                "effects": [
                    {k: e[k] for k in ("x", "y", "life", "color")}
                    for e in effects
                ]
            }

        socketio.emit("state", state)
        socketio.sleep(1/30)



# ================= NEON RUSH =================

race_players = {}
race_lock = RLock()
RACE_LAPS = 3
race_countdown = 0
race_started = False
race_finished = False
race_winner = None

def new_car(sid, name):
    index = len(race_players)
    return {
        "id": sid,
        "name": name,
        "x": 600 + index * 35,
        "y": 130 + index * 35,
        "angle": 0,
        "speed": 0,
        "lap": 0,
        "progress": 0,
        "previous": 0,
        "place": index + 1,
        "color": ["#00eaff", "#ff438e"][index % 2],
        "input": {},
        "finished": False
    }

@socketio.on("race_join")
def race_join(data):
    global race_countdown, race_started, race_finished, race_winner
    sid = request.sid
    with race_lock:
        if sid not in race_players and len(race_players) < 2 and not race_started:
            name = str(data.get("name", "Racer")).strip()[:16] or "Racer"
            race_players[sid] = new_car(sid, name)

        if sid in race_players:
            emit("race_joined", {"id": sid})
            if len(race_players) == 2:
                race_countdown = 4
                race_started = False
                race_finished = False
                race_winner = None

@socketio.on("race_input")
def race_input(data):
    with race_lock:
        p = race_players.get(request.sid)
        if p and not p["finished"]:
            p["input"] = {
                "up": bool(data.get("up")),
                "down": bool(data.get("down")),
                "left": bool(data.get("left")),
                "right": bool(data.get("right")),
                "drift": bool(data.get("drift"))
            }

@socketio.on("race_restart")
def race_restart():
    global race_countdown, race_started, race_finished, race_winner
    with race_lock:
        if request.sid not in race_players:
            return
        if len(race_players) < 2:
            emit("race_notice", {"text": "Čeká se na druhého závodníka."})
            return
        for i, p in enumerate(race_players.values()):
            p.update({
                "x": 600 + i * 35,
                "y": 130 + i * 35,
                "angle": 0,
                "speed": 0,
                "lap": 0,
                "progress": 0,
                "previous": 0,
                "finished": False
            })
        race_countdown = 4
        race_started = False
        race_finished = False
        race_winner = None

@socketio.on("race_leave")
def race_leave():
    global race_countdown, race_started
    with race_lock:
        race_players.pop(request.sid, None)
        race_started = False
        race_countdown = 0

def race_loop():
    global race_countdown, race_started, race_finished, race_winner

    previous = time.monotonic()
    countdown_timer = 0

    while True:
        now = time.monotonic()
        dt = min(now - previous, .04)
        previous = now

        with race_lock:
            if len(race_players) == 2 and not race_started and not race_finished:
                if race_countdown > 0:
                    countdown_timer += dt
                    if countdown_timer >= 1:
                        countdown_timer = 0
                        race_countdown -= 1
                else:
                    race_started = True
                    socketio.emit("race_notice", {"text": "START!"})

            if race_started and not race_finished:
                for p in race_players.values():
                    if p["finished"]:
                        continue

                    c = p["input"]
                    accelerating = c.get("up", False)
                    braking = c.get("down", False)
                    drifting = c.get("drift", False)

                    if accelerating:
                        p["speed"] += 360 * dt
                    elif braking:
                        p["speed"] -= 480 * dt
                    else:
                        p["speed"] *= max(0, 1 - 1.1 * dt)

                    p["speed"] = max(-100, min(410, p["speed"]))

                    steering = int(c.get("right", False)) - int(c.get("left", False))
                    turn = 2.3 if drifting else 1.65
                    p["angle"] += steering * turn * dt * min(1, abs(p["speed"])/100)

                    p["x"] += math.cos(p["angle"]) * p["speed"] * dt
                    p["y"] += math.sin(p["angle"]) * p["speed"] * dt

                    # Track detection
                    rx = (p["x"] - 600) / 390
                    ry = (p["y"] - 375) / 245
                    distance = math.sqrt(rx*rx + ry*ry)

                    if distance < .78 or distance > 1.18:
                        p["speed"] *= max(0, 1 - 2.5*dt)

                    p["x"] = max(20, min(1180, p["x"]))
                    p["y"] = max(20, min(730, p["y"]))

                    theta = math.atan2(ry, rx)
                    progress = ((theta + math.pi/2) % (2*math.pi)) / (2*math.pi)

                    if p["previous"] > .85 and progress < .15 and p["speed"] > 30:
                        p["lap"] += 1

                    p["previous"] = progress
                    p["progress"] = progress

                    if p["lap"] >= RACE_LAPS:
                        p["finished"] = True
                        if not race_finished:
                            race_finished = True
                            race_winner = p["name"]
                            socketio.emit("race_winner", {"name": race_winner})

            ordered = sorted(
                race_players.values(),
                key=lambda p: p["lap"] + p["progress"],
                reverse=True
            )

            state = {
                "players": [
                    {
                        "id": p["id"],
                        "name": p["name"],
                        "x": p["x"],
                        "y": p["y"],
                        "angle": p["angle"],
                        "speed": p["speed"],
                        "lap": p["lap"],
                        "color": p["color"],
                        "finished": p["finished"],
                        "place": i + 1
                    }
                    for i, p in enumerate(ordered)
                ],
                "countdown": race_countdown if not race_started else 0,
                "started": race_started,
                "finished": race_finished,
                "winner": race_winner
            }

        socketio.emit("race_state", state)
        socketio.sleep(1/30)


if __name__ == "__main__":
    socketio.start_background_task(game_loop)
    socketio.start_background_task(race_loop)
    print("="*40)
    print("       CYBER ARENA 2.0")
    print(" http://192.168.10.40:5000")
    print("="*40)
    socketio.run(app, host="0.0.0.0", port=5000)
