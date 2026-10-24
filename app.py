from datetime import datetime
import os
import pymysql
from flask import Flask, redirect, render_template_string, request, url_for

app = Flask(__name__)

# Konfigurasi Database dari Environment Variables Docker
DB_HOST = os.environ.get("DB_HOST", "db")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "rahsia_aman")
DB_NAME = os.environ.get("DB_NAME", "cloudvault_db")


def get_db_connection():
  return pymysql.connect(
      host=DB_HOST,
      user=DB_USER,
      password=DB_PASSWORD,
      database=DB_NAME,
      cursorclass=pymysql.cursors.DictCursor,
  )


def init_db():
  try:
    conn = pymysql.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS guestbook (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    conn.commit()
    cursor.close()
    conn.close()
  except Exception as e:
    print(f"Database init error: {e}")


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CloudVault & GuestHub | ISTN Jakarta</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; min-height: 100vh; padding-bottom: 40px; }
        .navbar-custom { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.1); }
        .card-custom { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .form-control { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.15); color: #fff; border-radius: 10px; }
        .form-control:focus { background: rgba(15, 23, 42, 0.8); border-color: #38bdf8; color: #fff; box-shadow: 0 0 0 0.25rem rgba(56, 189, 248, 0.25); }
        .btn-custom { background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%); border: none; border-radius: 10px; font-weight: 600; color: white; transition: all 0.3s ease; }
        .btn-custom:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(14, 165, 233, 0.4); color: white; }
        .table-custom { color: #f8fafc; }
        .table-custom th { background: rgba(15, 23, 42, 0.8); color: #38bdf8; border-color: rgba(255,255,255,0.1); }
        .table-custom td { background: rgba(30, 41, 59, 0.4); border-color: rgba(255,255,255,0.05); color: #e2e8f0; vertical-align: middle; }
        .table-custom td.text-time { color: #38bdf8 !important; font-weight: 600; }
    </style>
</head>
<body>
    <nav class="navbar navbar-custom py-3 mb-5">
        <div class="container">
            <span class="navbar-brand mb-0 h1 text-white fw-bold">
                <i class="fa-solid fa-cloud-arrow-up text-info me-2"></i> CloudVault & GuestHub
            </span>
            <span class="badge bg-primary bg-opacity-25 text-info border border-info px-3 py-2 rounded-pill">
                <i class="fa-solid fa-user-graduate me-1">></i> Putri Nurhaliza (24360002) - ISTN
            </span>
        </div>
    </nav>

    <div class="container">
        <div class="row justify-content-center mb-4">
            <div class="col-lg-10 text-center">
                <h2 class="fw-bold text-white mb-2">Sistem Buku Tamu Terdistribusi</h2>
                <p class="text-secondary">Praktikum Komputasi Awan dan Terdistribusi • Docker Multi-Container Architecture</p>
            </div>
        </div>

        <div class="row g-4">
            <!-- Form Input -->
            <div class="col-lg-4">
                <div class="card card-custom p-4 h-100">
                    <h4 class="mb-3 text-white fw-semibold"><i class="fa-solid fa-pen-to-square text-info me-2"></i> Kirim Pesan</h4>
                    <form method="POST" action="/">
                        <div class="mb-3">
                            <label class="form-label text-secondary small fw-semibold">NAMA LENGKAP</label>
                            <input type="text" name="name" class="form-control" placeholder="Contoh: Putri Nurhaliza" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label text-secondary small fw-semibold">PESAN / KESAN PRAKTIKUM</label>
                            <textarea name="message" class="form-control" rows="4" placeholder="Tuliskan kesan pesan praktikum Anda..." required></textarea>
                        </div>
                        <button type="submit" class="btn btn-custom w-100 py-2"><i class="fa-solid fa-paper-plane me-2"></i> Kirim ke Cloud Database</button>
                    </form>
                </div>
            </div>

            <!-- Tabel Data -->
            <div class="col-lg-8">
                <div class="card card-custom p-4 h-100">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h4 class="text-white fw-semibold m-0"><i class="fa-solid fa-database text-info me-2"></i> Log Catatan Tersimpan</h4>
                        <span class="badge bg-secondary px-3 py-2">Total: {{ entries|length }} Entri</span>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-custom table-hover align-middle rounded overflow-hidden">
                            <thead>
                                <tr>
                                    <th style="width: 25%;">Pengunjung</th>
                                    <th style="width: 50%;">Pesan</th>
                                    <th style="width: 25%;">Waktu</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% if entries %}
                                    {% for entry in entries %}
                                    <tr>
                                        <td class="fw-bold text-info"><i class="fa-solid fa-user-circle me-1"></i> {{ entry.name }}</td>
                                        <td>{{ entry.message }}</td>
                                        <td class="text-time small">{{ entry.created_at.strftime('%Y-%m-%d %H:%M:%S') }}</td>
                                    </tr>
                                    {% endfor %}
                                {% else %}
                                    <tr>
                                        <td colspan="3" class="text-center text-secondary py-4">Belum ada catatan data tersimpan di database.</td>
                                    </tr>
                                {% endif %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
  if request.method == "POST":
    name = request.form.get("name")
    message = request.form.get("message")
    if name and message:
      try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO guestbook (name, message) VALUES (%s, %s)",
            (name, message),
        )
        conn.commit()
        cursor.close()
        conn.close()
      except Exception as e:
        print(f"Insert error: {e}")
    return redirect(url_for("index"))

  entries = []
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM guestbook ORDER BY id DESC")
    entries = cursor.fetchall()
    cursor.close()
    conn.close()
  except Exception as e:
    print(f"Fetch error: {e}")

  return render_template_string(HTML_TEMPLATE, entries=entries)


if __name__ == "__main__":
  init_db()
  app.run(host="0.0.0.0", port=5000, debug=True)