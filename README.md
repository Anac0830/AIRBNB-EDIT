# PDF Value Editor

Edit money values and text in PDFs without changing the layout.  
Built with Flask + PyMuPDF. Ready to deploy on **Render.com** in 2 minutes.

---

## 🚀 Deploy to Render.com (Free)

1. Push this folder to a **GitHub repo** (new private repo works fine)
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` — just click **Deploy**
5. Your app will be live at `https://your-app.onrender.com`

---

## 💻 Run locally

```bash
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

---

## ✨ Features

- **Auto-detect** money values in any PDF with one click
- **Find & Replace** any text while preserving layout
- Supports Airbnb, VRBO, and any browser-printed PDF
- Multiple replacements in one pass
- Download the edited PDF instantly

---

## 📁 Structure

```
pdf-editor/
├── app.py              # Flask backend
├── requirements.txt    # Python dependencies
├── Procfile            # For Render/Heroku
├── render.yaml         # Render.com config
└── templates/
    └── index.html      # Frontend UI
```
