"""
Script lam sach va chuan hoa du lieu CSV tu Kaggle
de tuong thich voi Music Recommendation Engine.

Cach su dung:
    python clean_kaggle_data.py <duong_dan_file_kaggle.csv>

Ket qua:
    File tracks.csv moi duoc tao trong thu muc backend/data/

Ho tro 2 loai dataset:
  A) Dataset CO metadata (track_name, artist_name, genre, year)
     -> Map cot va chuan hoa binh thuong
  B) Dataset CHI CO audio features (danceability, energy, ...)
     -> Tu dong phan loai genre dua tren audio features
     -> Sinh ten bai hat va nghe si tu dong
"""

import pandas as pd
import numpy as np
import sys
import os

# ============================================================
# Cac ten cot ma he thong can
# ============================================================
REQUIRED_COLUMNS = {
    "id": ["id", "track_id", "song_id", "index"],
    "track_name": ["track_name", "track", "name", "song_name", "title"],
    "artist_name": ["artist_name", "artist", "artists", "artist(s)", "performer", "channel"],
    "genre": ["genre", "track_genre", "top genre", "genre_top", "category", "music_genre"],
    "year": ["year", "release_year", "release_date", "released_year"],
    "danceability": ["danceability", "danceability_%"],
    "energy": ["energy", "energy_%"],
    "valence": ["valence", "valence_%"],
    "tempo": ["tempo", "bpm"],
    "acousticness": ["acousticness", "acousticness_%"],
    "instrumentalness": ["instrumentalness", "instrumentalness_%"],
    "liveness": ["liveness", "liveness_%"],
    "speechiness": ["speechiness", "speechiness_%"],
}

AUDIO_FEATURES = [
    "danceability", "energy", "valence", "tempo",
    "acousticness", "instrumentalness", "liveness", "speechiness"
]

# Cac feature can nam trong khoang [0, 1] (tru tempo)
NORMALIZED_FEATURES = [
    "danceability", "energy", "valence",
    "acousticness", "instrumentalness", "liveness", "speechiness"
]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "tracks.csv")


def find_column(df_columns, target, aliases):
    """Tim ten cot tuong ung trong DataFrame"""
    lower_cols = {c.lower().strip(): c for c in df_columns}
    for alias in aliases:
        if alias.lower() in lower_cols:
            return lower_cols[alias.lower()]
    return None


def classify_genre(row):
    """
    Phan loai genre tu dong dua tren audio features.
    Dung cac nguong don gian de chia thanh cac nhom nhac pho bien.
    """
    dance = row.get("danceability", 0)
    energy = row.get("energy", 0)
    valence = row.get("valence", 0)
    acousticness = row.get("acousticness", 0)
    instrumentalness = row.get("instrumentalness", 0)
    speechiness = row.get("speechiness", 0)
    tempo = row.get("tempo", 120)

    # Classical: nhac khong loi, acoustic cao, nang luong thap
    if instrumentalness > 0.5 and acousticness > 0.5 and energy < 0.4:
        return "Classical"

    # Jazz: acoustic cao, instrumentalness trung binh, tempo cham-vua
    if acousticness > 0.4 and instrumentalness > 0.1 and energy < 0.6 and tempo < 140:
        return "Jazz"

    # Electronic: instrumentalness cao, energy cao, acoustic thap
    if instrumentalness > 0.3 and acousticness < 0.3 and energy > 0.5:
        return "Electronic"

    # Hip-Hop: speechiness cao, danceability cao
    if speechiness > 0.15 and dance > 0.6:
        return "Hip-Hop"

    # R&B: danceability vua-cao, valence trung binh, acoustic vua
    if dance > 0.5 and acousticness > 0.2 and energy < 0.7 and speechiness < 0.15:
        return "R&B"

    # Folk: acoustic cao, energy thap-vua
    if acousticness > 0.5 and energy < 0.6:
        return "Folk"

    # Rock: energy cao, acoustic thap
    if energy > 0.7 and acousticness < 0.3 and dance < 0.6:
        return "Rock"

    # Pop: danceability cao, valence cao, energy vua-cao
    if dance > 0.5 and valence > 0.4:
        return "Pop"

    # Latin: danceability rat cao, tempo nhanh
    if dance > 0.7 and tempo > 130:
        return "Latin"

    # Mac dinh
    return "Pop"


def generate_track_name(idx, row):
    """Sinh ten bai hat tu dong dua tren dac trung am nhac"""
    energy = row.get("energy", 0.5)
    valence = row.get("valence", 0.5)
    tempo = row.get("tempo", 120)

    # Chon mood word
    if valence > 0.7 and energy > 0.7:
        moods = ["Euphoria", "Sunshine", "Celebration", "Radiance", "Spark"]
    elif valence > 0.5 and energy > 0.5:
        moods = ["Breeze", "Glow", "Pulse", "Motion", "Wave"]
    elif valence < 0.3 and energy < 0.4:
        moods = ["Shadow", "Whisper", "Solitude", "Drift", "Echo"]
    elif valence < 0.4:
        moods = ["Rain", "Twilight", "Dusk", "Mist", "Silence"]
    elif energy > 0.7:
        moods = ["Thunder", "Storm", "Blaze", "Ignite", "Rush"]
    else:
        moods = ["Dream", "Horizon", "Flow", "Moment", "Path"]

    mood_word = moods[idx % len(moods)]

    # Them so thu tu de dam bao duy nhat
    return f"{mood_word} #{idx + 1:03d}"


def generate_artist_name(idx, genre):
    """Sinh ten nghe si tu dong"""
    # Tao nhom nghe si (moi nhom 5-8 bai hat) de co su lap lai tu nhien
    artists_by_genre = {
        "Pop": ["Luna", "Aria", "Nova", "Stella", "Vivian", "Melody"],
        "Rock": ["Onyx", "Blaze", "Rex", "Ace", "Jett", "Knox"],
        "Hip-Hop": ["Kyro", "Zane", "Dex", "Nyx", "Flux", "Vex"],
        "R&B": ["Soleil", "Jade", "Raven", "Sienna", "Ivory", "Amara"],
        "Electronic": ["Pixel", "Neon", "Cypher", "Volt", "Hexa", "Grid"],
        "Jazz": ["Miles", "Ella", "Chet", "Nina", "Duke", "Billie"],
        "Classical": ["Opus", "Adagio", "Forte", "Lyra", "Cadence", "Allegra"],
        "Folk": ["Ivy", "Cedar", "Sage", "Willow", "Hazel", "Rowan"],
        "Latin": ["Rio", "Sol", "Fuego", "Luna", "Cielo", "Alma"],
    }
    artists = artists_by_genre.get(genre, ["Artist"])
    group_idx = (idx // 5) % len(artists)
    return artists[group_idx]


def clean_kaggle_csv(input_path):
    """Doc va chuan hoa file CSV tu Kaggle"""
    print(f"\n{'='*60}")
    print(f"  Clean Kaggle Data -> Music Recommendation System")
    print(f"{'='*60}")
    print(f"  Input:  {input_path}")
    print(f"  Output: {OUTPUT_FILE}")
    print(f"{'='*60}\n")

    # Buoc 1: Doc file CSV
    print("[1/6] Doc file CSV...")
    try:
        df = pd.read_csv(input_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(input_path, encoding="latin-1")
    print(f"  -> {len(df)} dong, {len(df.columns)} cot")
    print(f"  -> Cac cot: {list(df.columns)}")

    # Buoc 2: Map ten cot
    print("\n[2/6] Map ten cot...")
    column_mapping = {}
    missing = []
    for target, aliases in REQUIRED_COLUMNS.items():
        found = find_column(df.columns, target, aliases)
        if found:
            column_mapping[found] = target
            print(f"  {target:20s} <- '{found}'")
        else:
            missing.append(target)
            print(f"  {target:20s} <- KHONG TIM THAY")

    # Doi ten cac cot da tim thay
    df = df.rename(columns=column_mapping)

    # Kiem tra xem co du 8 audio features khong
    audio_missing = [f for f in AUDIO_FEATURES if f not in df.columns]
    if audio_missing:
        print(f"\n  LOI: Thieu cac audio features bat buoc: {audio_missing}")
        print(f"  Khong the tiep tuc.")
        sys.exit(1)

    # Chuyen doi audio features sang so truoc
    for feat in NORMALIZED_FEATURES + ["tempo"]:
        df[feat] = pd.to_numeric(df[feat], errors="coerce")

    # Neu features dang o dang % (0-100), chuan hoa ve [0, 1]
    for feat in NORMALIZED_FEATURES:
        col = df[feat].dropna()
        if len(col) > 0 and col.max() > 1.0:
            print(f"  -> Chuan hoa {feat}: {col.min():.1f}-{col.max():.1f} -> 0.0-1.0")
            df[feat] = df[feat] / 100.0

    # Xoa dong thieu audio features
    before = len(df)
    df = df.dropna(subset=AUDIO_FEATURES)
    if before - len(df) > 0:
        print(f"  -> Xoa {before - len(df)} dong thieu audio features")

    # Xac dinh che do: co metadata hay chi co features
    metadata_missing = [m for m in missing if m in ("track_name", "artist_name", "genre", "year")]
    features_only_mode = len(metadata_missing) > 0

    if features_only_mode:
        print(f"\n  ** CHE DO: Chi co audio features (thieu: {metadata_missing})")
        print(f"  ** Se tu dong sinh metadata tu audio features **")

    # Buoc 3: Tao/xu ly metadata
    print("\n[3/6] Xu ly metadata...")

    if "id" in missing:
        df["id"] = range(1, len(df) + 1)
        print("  -> Tu dong tao cot 'id'")

    if "genre" not in df.columns or "genre" in metadata_missing:
        print("  -> Tu dong phan loai genre dua tren audio features...")
        df["genre"] = df.apply(classify_genre, axis=1)
        genre_counts = df["genre"].value_counts()
        for g, c in genre_counts.items():
            print(f"     {g:15s}: {c} bai hat")

    if "track_name" not in df.columns or "track_name" in metadata_missing:
        print("  -> Tu dong sinh ten bai hat...")
        df["track_name"] = [generate_track_name(i, df.iloc[i]) for i in range(len(df))]

    if "artist_name" not in df.columns or "artist_name" in metadata_missing:
        print("  -> Tu dong sinh ten nghe si...")
        df["artist_name"] = [generate_artist_name(i, df.iloc[i]["genre"]) for i in range(len(df))]
        print(f"     -> {df['artist_name'].nunique()} nghe si")

    if "year" not in df.columns or "year" in metadata_missing:
        df["year"] = 2023
        print("  -> Dat year mac dinh: 2023")
    else:
        # Xu ly year: neu la date string thi lay nam
        if df["year"].dtype == object:
            df["year"] = pd.to_datetime(df["year"], errors="coerce").dt.year
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df = df.dropna(subset=["year"])
        df["year"] = df["year"].astype(int)
        print(f"  -> Year range: {df['year'].min()} - {df['year'].max()}")

    # Buoc 4: Chuan hoa du lieu
    print("\n[4/6] Chuan hoa du lieu...")

    # Tempo: giu nguyen BPM (thuong 50-250)
    tempo_col = df["tempo"].dropna()
    if len(tempo_col) > 0:
        print(f"  -> Tempo (BPM): {tempo_col.min():.0f} - {tempo_col.max():.0f}")

    # In thong ke features
    for feat in NORMALIZED_FEATURES:
        col = df[feat].dropna()
        print(f"  -> {feat:20s}: {col.min():.3f} - {col.max():.3f} (mean: {col.mean():.3f})")

    # Buoc 5: Loc va lam sach
    print("\n[5/6] Loc va lam sach...")

    # Xoa dong thieu thong tin co ban
    before = len(df)
    df = df.dropna(subset=["track_name", "artist_name", "genre"])
    dropped = before - len(df)
    if dropped > 0:
        print(f"  -> Xoa {dropped} dong thieu ten/nghe si/genre")

    # Xoa trung lap
    before = len(df)
    df = df.drop_duplicates(subset=["track_name", "artist_name"])
    dropped = before - len(df)
    if dropped > 0:
        print(f"  -> Xoa {dropped} dong trung lap")

    # Reset index va ID
    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    print(f"  -> Con lai: {len(df)} bai hat")

    # Buoc 6: Luu ket qua
    print("\n[6/6] Luu ket qua...")
    output_cols = [
        "id", "track_name", "artist_name", "genre", "year",
        "danceability", "energy", "valence", "tempo",
        "acousticness", "instrumentalness", "liveness", "speechiness"
    ]

    # Giu them cot 'popularity' hoac 'liked' neu co
    if "popularity" in df.columns:
        output_cols.append("popularity")
        print("  -> Giu them cot 'popularity'")
    if "liked" in df.columns:
        output_cols.append("liked")
        print("  -> Giu them cot 'liked'")

    df_out = df[output_cols]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df_out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"  HOAN THANH!")
    print(f"  -> {len(df_out)} bai hat da luu vao {OUTPUT_FILE}")
    print(f"  -> Genres: {sorted(df_out['genre'].unique().tolist())}")
    print(f"  -> Nam: {df_out['year'].min()} - {df_out['year'].max()}")
    print(f"  -> Artists: {df_out['artist_name'].nunique()}")
    print(f"{'='*60}")
    print(f"\n  Buoc tiep theo:")
    print(f"  1. Khoi dong lai backend: python app.py")
    print(f"  2. Kiem tra: http://localhost:5000/api/stats")

    if features_only_mode:
        print(f"\n  LUU Y: Dataset goc chi co audio features, metadata")
        print(f"  (ten bai hat, nghe si, genre) da duoc sinh tu dong.")
        print(f"  De ket qua tot hon, hay dung dataset co day du metadata.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cach su dung: python clean_kaggle_data.py <duong_dan_file.csv>")
        print("\nVi du:")
        print("  python clean_kaggle_data.py C:\\Users\\Downloads\\spotify_songs.csv")
        print("  python clean_kaggle_data.py backend/data/dataset.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"LOI: Khong tim thay file: {input_file}")
        sys.exit(1)

    clean_kaggle_csv(input_file)
