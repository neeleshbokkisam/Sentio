import csv
import io
import sqlite3
from collections import Counter
from datetime import datetime, timedelta

from modules.config import DB_PATH


def list_sessions(limit: int = 50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT s.*,
                  COUNT(r.id) as reading_count,
                  (SELECT mood FROM readings WHERE session_id = s.id
                   GROUP BY mood ORDER BY COUNT(*) DESC LIMIT 1) as top_mood
           FROM sessions s
           LEFT JOIN readings r ON r.session_id = s.id
           GROUP BY s.id
           ORDER BY s.started_at DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_session_replay(session_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    session = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    readings = conn.execute(
        "SELECT * FROM readings WHERE session_id = ? ORDER BY timestamp",
        (session_id,),
    ).fetchall()
    conn.close()
    if not session:
        return None
    return {"session": dict(session), "readings": [dict(r) for r in readings]}


def daily_insights():
    today = datetime.now().date().isoformat()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT mood FROM readings WHERE date(timestamp) = ?",
        (today,),
    ).fetchall()
    conn.close()
    moods = [r[0].split("/")[0] for r in rows]
    counts = Counter(moods)
    return {"date": today, "counts": dict(counts), "total": len(moods)}


def weekly_insights():
    start = (datetime.now() - timedelta(days=6)).date().isoformat()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """SELECT date(timestamp) as day, mood
           FROM readings WHERE date(timestamp) >= ?
           ORDER BY timestamp""",
        (start,),
    ).fetchall()
    conn.close()

    by_day = {}
    for day, mood in rows:
        by_day.setdefault(day, []).append(mood.split("/")[0])

    trend = []
    for day in sorted(by_day.keys()):
        top = Counter(by_day[day]).most_common(1)
        trend.append({"day": day, "mood": top[0][0] if top else "neutral", "count": len(by_day[day])})
    return {"days": trend}


def export_session_csv(session_id: int) -> str:
    data = get_session_replay(session_id)
    if not data:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["timestamp", "face", "face_conf", "voice", "voice_conf", "mood", "mismatch"],
    )
    writer.writeheader()
    for row in data["readings"]:
        writer.writerow({
            "timestamp": row["timestamp"],
            "face": row["face"],
            "face_conf": row["face_conf"],
            "voice": row["voice"],
            "voice_conf": row["voice_conf"],
            "mood": row["mood"],
            "mismatch": row["mismatch"],
        })
    return output.getvalue()
