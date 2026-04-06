"""
Flask API Server - Music Recommendation System
REST API cung cap cac endpoint cho frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from engine import RecommendationEngine

# ============================================================
# Khoi tao Flask app & CORS
# ============================================================
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Khoi tao Recommendation Engine
engine = RecommendationEngine()


# ============================================================
# API ENDPOINTS
# ============================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """Kiem tra trang thai server"""
    return jsonify({"status": "ok", "message": "Music Recommendation API is running"})


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Thong ke tong quat ve dataset"""
    stats = engine.get_stats()
    return jsonify({"success": True, "data": stats})


@app.route("/api/tracks", methods=["GET"])
def get_tracks():
    """
    Lay danh sach bai hat
    Query params:
        - q: tu khoa tim kiem (optional)
        - limit: so luong ket qua (default: 20)
    """
    query = request.args.get("q", "").strip()
    limit = request.args.get("limit", 20, type=int)

    if query:
        tracks = engine.search_tracks(query, limit=limit)
    else:
        tracks = engine.get_all_tracks()[:limit]

    return jsonify({"success": True, "data": tracks, "total": len(tracks)})


@app.route("/api/tracks/<int:track_id>", methods=["GET"])
def get_track_detail(track_id):
    """Lay chi tiet 1 bai hat kem audio features"""
    result = engine.get_track_features(track_id)
    if result is None:
        return jsonify({"success": False, "error": "Track not found"}), 404
    return jsonify({"success": True, "data": result})


@app.route("/api/genres", methods=["GET"])
def get_genres():
    """Lay danh sach the loai nhac"""
    genres = engine.get_genres()
    return jsonify({"success": True, "data": genres})


@app.route("/api/moods", methods=["GET"])
def get_moods():
    """Lay danh sach tam trang"""
    moods = engine.get_moods()
    return jsonify({"success": True, "data": moods})


@app.route("/api/recommend", methods=["POST"])
def recommend():
    """
    Goi y nhac dua tren bai hat nguoi dung chon
    
    Request body (JSON):
    {
        "track_id": 1,         // ID bai hat da chon (bat buoc)
        "genre": "Pop",        // Loc theo the loai (optional)
        "mood": "happy",       // Loc theo tam trang (optional)
        "top_n": 10            // So luong goi y (optional, default: 10)
    }
    
    Response:
    {
        "success": true,
        "data": {
            "source_track": {...},
            "recommendations": [...],
            "filters": {"genre": "Pop", "mood": "happy"},
            "total": 10
        }
    }
    """
    data = request.get_json()

    if not data or "track_id" not in data:
        return jsonify({
            "success": False,
            "error": "Missing required field: track_id"
        }), 400

    track_id = data["track_id"]
    genre = data.get("genre", None)
    mood = data.get("mood", None)
    top_n = data.get("top_n", 10)

    # Kiem tra bai hat co ton tai khong
    source_track = engine.get_track_by_id(track_id)
    if source_track is None:
        return jsonify({
            "success": False,
            "error": f"Track with id={track_id} not found"
        }), 404

    # Goi y nhac
    recommendations = engine.recommend(
        track_id=track_id,
        genre=genre,
        mood=mood,
        top_n=top_n
    )

    return jsonify({
        "success": True,
        "data": {
            "source_track": source_track,
            "recommendations": recommendations,
            "filters": {
                "genre": genre,
                "mood": mood
            },
            "total": len(recommendations)
        }
    })


@app.route("/api/recommend/batch", methods=["POST"])
def recommend_batch():
    """
    Goi y nhac dua tren nhieu bai hat (user profile)
    
    Request body (JSON):
    {
        "track_ids": [1, 2, 3],  // Danh sach ID bai hat da thich
        "genre": "Pop",
        "mood": "happy",
        "top_n": 10
    }
    """
    data = request.get_json()

    if not data or "track_ids" not in data:
        return jsonify({
            "success": False,
            "error": "Missing required field: track_ids"
        }), 400

    track_ids = data["track_ids"]
    genre = data.get("genre", None)
    mood = data.get("mood", None)
    top_n = data.get("top_n", 10)

    # Gom tat ca goi y tu cac bai hat
    all_recs = {}
    for tid in track_ids:
        recs = engine.recommend(track_id=tid, genre=genre, mood=mood, top_n=top_n * 2)
        for r in recs:
            rid = r["id"]
            if rid not in track_ids:  # Loai bo bai hat da chon
                if rid not in all_recs or r["similarity"] > all_recs[rid]["similarity"]:
                    all_recs[rid] = r

    # Sap xep va lay top N
    sorted_recs = sorted(all_recs.values(), key=lambda x: x["similarity"], reverse=True)[:top_n]

    return jsonify({
        "success": True,
        "data": {
            "source_track_ids": track_ids,
            "recommendations": sorted_recs,
            "total": len(sorted_recs)
        }
    })


# ============================================================
# Error handlers
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": "Internal server error"}), 500


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  Music Recommendation API Server")
    print("  http://localhost:5000")
    print("=" * 60)
    print(f"  Dataset: {engine.get_stats()['total_tracks']} tracks")
    print(f"  Genres:  {engine.get_stats()['total_genres']}")
    print(f"  Artists: {engine.get_stats()['total_artists']}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)
