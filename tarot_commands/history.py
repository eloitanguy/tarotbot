import json
from datetime import datetime


def update_history(scores):
    with open('history.json', 'r') as f:
        HISTORY = json.load(f)

    next_entry = {
        'time': datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
        'scores': scores
    }

    HISTORY.append(next_entry)

    with open('history.json', 'w') as f:
        json.dump(HISTORY, f, indent=4)
