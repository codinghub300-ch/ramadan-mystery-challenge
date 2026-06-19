import hashlib
import json
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
import hashlib
import os



Salt_key= "525aeb0bd3c8c6e745aa47a19dd029ed"
Hash="f9db9403c08ab439c5502dc5a208e34234fedf0dc5088614cd786da602bd8421"
SECRET_KEY = "J4XHW-F3OQD-YD6KS"+Salt_key+Hash
SECRET_HASH = hashlib.sha256(SECRET_KEY.encode()).hexdigest()

WINNERS_FILE = "winners.json"
LOG_FILE = "attempts.log"

rate_limit = {}
block_map = {}
fail_counter = {}

def load_winners():
    with open(WINNERS_FILE, "r") as f:
        return json.load(f)["winners"]

def save_winners(winners):
    with open(WINNERS_FILE, "w") as f:
        json.dump({"winners": winners}, f, indent=4)

def log_attempt(data):
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lantern")
def lantern():
    return render_template("lantern.html")

@app.route("/leaderboard")
def leaderboard():
    winners = load_winners()
    winners = sorted(winners, key=lambda x: x["rank"])
    return render_template("leaderboard.html", winners=winners)

@app.route("/submit", methods=["POST"])
def submit():
    ip = request.remote_addr
    key = request.json.get("key", "")
    now = time.time()

    if ip in block_map and now < block_map[ip]:
        return jsonify({"message": "Too many attempts. Try later."}), 403

    if ip in rate_limit and now - rate_limit[ip] < 5:
        return jsonify({"message": "Slow down."}), 429

    rate_limit[ip] = now
    winners = load_winners()

    if len(winners) >= 3:
        return jsonify({"message": "Lantern already claimed."})

    attempt_hash = hashlib.sha256(key.encode()).hexdigest()

    if attempt_hash == SECRET_HASH:
        rank = len(winners) + 1
        points = 60 if rank == 1 else 30 if rank == 2 else 15

        winner_data = {
            "ip": ip,
            "time": datetime.utcnow().isoformat(),
            "rank": rank,
            "points": points
        }

        winners.append(winner_data)
        save_winners(winners)

        log_attempt({"ip": ip, "time": datetime.utcnow().isoformat(), "status": "SUCCESS"})

        return jsonify({"success": True, "rank": rank, "points": points})

    else:
        fail_counter[ip] = fail_counter.get(ip, 0) + 1

        if fail_counter[ip] >= 20:
            block_map[ip] = now + (20 * 60)

        log_attempt({"ip": ip, "time": datetime.utcnow().isoformat(), "status": "FAIL"})

        return jsonify({"success": False})

# if __name__ == "__main__":
#     import os
#     port = int(os.environ.get("PORT", 8080))
#     app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    
