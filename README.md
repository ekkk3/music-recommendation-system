# Music Recommendation System
## He thong goi y nhac dua tren thong tin ca nhan

> Chuyen de He thong Tin — Content-based Filtering + Cosine Similarity

---

## Kien truc he thong

```
music-recommendation-system/
│
├── backend/                    # Python Flask API Server
│   ├── app.py                  # Flask server + REST API endpoints
│   ├── engine.py               # Recommendation Engine (ML logic)
│   ├── requirements.txt        # Python dependencies
│   └── data/
│       └── tracks.csv          # Dataset (80 bai hat, Spotify features)
│
├── frontend/                   # React.js Client
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx             # Main application component
│   │   ├── App.css             # Global styles
│   │   ├── index.js            # React entry point
│   │   ├── services/
│   │   │   └── api.js          # API service layer (fetch wrapper)
│   │   └── components/
│   │       ├── SearchBar.jsx / .css
│   │       ├── StepIndicator.jsx / .css
│   │       ├── TrackCard.jsx / .css
│   │       ├── FilterPanel.jsx / .css
│   │       └── FeatureChart.jsx / .css
│   ├── .env                    # Environment variables
│   └── package.json
│
└── README.md
```

---

## Cong nghe su dung

| Layer     | Cong nghe              | Muc dich                          |
|-----------|------------------------|-----------------------------------|
| Backend   | Python 3.10+           | Ngon ngu chinh                    |
| Backend   | Flask 3.1              | REST API framework                |
| Backend   | Flask-CORS             | Cross-Origin Resource Sharing     |
| Backend   | Pandas                 | Xu ly du lieu                     |
| Backend   | NumPy                  | Tinh toan so hoc                  |
| Backend   | Scikit-learn           | MinMaxScaler, Cosine Similarity   |
| Frontend  | React 18               | UI framework                      |
| Frontend  | CSS3                   | Styling (custom, khong dung lib)  |
| Dataset   | CSV (Spotify features) | 80 bai hat, 8 audio features     |

---

## Cai dat & Chay

### 1. Backend (Python Flask)

```bash
# Di chuyen vao thu muc backend
cd backend

# Tao virtual environment (khuyen nghi)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate         # Windows

# Cai dat dependencies
pip install -r requirements.txt

# Chay server
python app.py
```

Server se chay tai: **http://localhost:5000**

### 2. Frontend (React)

```bash
# Mo terminal moi, di chuyen vao thu muc frontend
cd frontend

# Cai dat dependencies
npm install

# Chay development server
npm start
```

App se chay tai: **http://localhost:3000**

---

## API Endpoints

| Method | Endpoint              | Mo ta                                |
|--------|-----------------------|--------------------------------------|
| GET    | `/api/health`         | Kiem tra trang thai server           |
| GET    | `/api/stats`          | Thong ke dataset                     |
| GET    | `/api/tracks`         | Danh sach bai hat (?q=search&limit=) |
| GET    | `/api/tracks/:id`     | Chi tiet 1 bai hat + features        |
| GET    | `/api/genres`         | Danh sach the loai                   |
| GET    | `/api/moods`          | Danh sach tam trang                  |
| POST   | `/api/recommend`      | Goi y nhac tu 1 bai hat             |
| POST   | `/api/recommend/batch`| Goi y nhac tu nhieu bai hat          |

### Vi du goi API recommend:

```bash
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"track_id": 2, "genre": "Pop", "mood": "happy", "top_n": 5}'
```

---

## Thuat toan

### Content-based Filtering

1. **Trich xuat dac trung**: 8 audio features tu moi bai hat
2. **Chuan hoa**: MinMaxScaler → tat ca features ve [0, 1]
3. **Tinh Cosine Similarity**: Ma tran NxN do tuong dong giua moi cap bai hat
4. **Loc & xep hang**: Loc theo genre/mood → sap xep theo similarity giam dan → top-N

### Cosine Similarity

```
cos(A, B) = (A · B) / (||A|| × ||B||)
```

Gia tri trong [0, 1]: 1 = giong hoan toan, 0 = hoan toan khac.

---

## Dataset

Dataset hien tai sử dụng https://www.kaggle.com/datasets/sanjanchaudhari/spotify-dataset bai hat voi cac features mo phong theo Spotify API.


---

## Thanh vien nhom

| STT | Ho ten        | MSSV     | Nhiem vu                              |
|-----|---------------|----------|---------------------------------------|
| 1   | Thanh vien 1  | xxxxxxxx | Thu thap & xu ly du lieu, EDA         |
| 2   | Thanh vien 2  | xxxxxxxx | Xay dung mo hinh ML, Backend API     |
| 3   | Thanh vien 3  | xxxxxxxx | Frontend React, Tich hop, Bao cao    |
