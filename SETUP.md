# Setup Guide - Webshop Project

Vollständige Anleitung zum Einrichten des Django-Webshop-Projekts auf einem neuen System.

---

## 📋 Voraussetzungen

- **Docker Desktop** installiert und laufend
- **Git** installiert
- **Python 3.13+** (optional, für lokale Entwicklung)
- Terminal/PowerShell Zugriff

---

## 🚀 Schnellstart (5 Minuten)

### 1. Repository klonen

```bash
git clone https://github.com/hieni/Challenge-III-Webshop.git
cd Challenge-III-Webshop/webshop
```

### 2. Docker Container starten

```bash
docker compose up --build
```

**Was passiert:**
- PostgreSQL 17 Datenbank wird gestartet
- Django App wird gebaut und gestartet
- Datenbank-Migrationen werden ausgeführt
- Superuser `admin` wird erstellt (Passwort: `1234`)
- Fixture-Daten werden geladen (Kategorien, Produkte)

### 3. Webshop öffnen

Browser öffnen: **http://localhost:8000**

**Fertig!** 🎉

---

## 📦 Detaillierte Setup-Schritte

### Option A: Mit Docker (Empfohlen für Produktion)

#### 1. Projekt klonen
```bash
git clone https://github.com/hieni/Challenge-III-Webshop.git
cd Challenge-III-Webshop/webshop
```

#### 2. Environment-Variablen (optional)

Erstelle eine `.env` Datei im `webshop/` Verzeichnis:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=1

# PostgreSQL
POSTGRES_DB=webshop_db
POSTGRES_USER=webshop_user
POSTGRES_PASSWORD=webshop_pass
DB_HOST=db
DB_PORT=5432
```

**Hinweis:** Die Defaults in `compose.yml` funktionieren auch ohne `.env`.

#### 3. Container bauen und starten
```bash
# Erste Ausführung (mit Build)
docker compose up --build

# Oder im Hintergrund
docker compose up -d --build
```

#### 4. Logs überprüfen
```bash
# Live-Logs verfolgen
docker compose logs -f web

# Letzte 50 Zeilen
docker compose logs web --tail=50
```

#### 5. Admin-Panel zugreifen

**URL:** http://localhost:8000/admin

**Login:**
- Username: `admin`
- Passwort: `1234`

---

### Option B: Lokale Entwicklung (ohne Docker)

#### 1. Virtual Environment erstellen

**Windows (PowerShell):**
```powershell
cd Challenge-III-Webshop/webshop
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
cd Challenge-III-Webshop/webshop
python3 -m venv .venv
source .venv/bin/activate
```

#### 2. Dependencies installieren
```bash
pip install -r requirements.txt
```

#### 3. PostgreSQL starten (nur DB-Container)
```bash
docker compose up db -d
```

#### 4. Environment-Variablen setzen

**Windows (PowerShell):**
```powershell
$env:DJANGO_SECRET_KEY="dev-secret-key"
$env:DEBUG="1"
$env:DB_NAME="webshop_db"
$env:DB_USER="webshop_user"
$env:DB_PASSWORD="webshop_pass"
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
```

**Linux/Mac:**
```bash
export DJANGO_SECRET_KEY="dev-secret-key"
export DEBUG="1"
export DB_NAME="webshop_db"
export DB_USER="webshop_user"
export DB_PASSWORD="webshop_pass"
export DB_HOST="localhost"
export DB_PORT="5432"
```

#### 5. Datenbank migrieren
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Superuser erstellen
```bash
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: 1234 (oder eigenes Passwort)
```

#### 7. Fixtures laden
```bash
python manage.py loaddata shop/fixtures/data.yaml
```

#### 8. Static Files sammeln
```bash
python manage.py collectstatic --noinput
```

#### 9. Development Server starten
```bash
python manage.py runserver
```

**URL:** http://localhost:8000

---

## 🔧 Nützliche Befehle

### Docker Container Management

```bash
# Container starten
docker compose up

# Container im Hintergrund starten
docker compose up -d

# Container stoppen
docker compose down

# Container mit Datenbank-Reset
docker compose down -v
docker compose up --build

# In Web-Container einloggen
docker exec -it webshop-web-1 bash

# Django Shell im Container
docker compose exec web python manage.py shell

# Neue Migration erstellen
docker compose exec web python manage.py makemigrations

# Migrationen anwenden
docker compose exec web python manage.py migrate
```

### Django Management

```bash
# Superuser erstellen
docker compose exec web python manage.py createsuperuser

# Django Shell öffnen
docker compose exec web python manage.py shell

# Tests ausführen
docker compose exec web python manage.py test

# Daten exportieren
docker compose exec web python manage.py dumpdata shop > backup.json

# Daten importieren
docker compose exec web python manage.py loaddata backup.json
```

### Datenbank

```bash
# PostgreSQL Shell öffnen
docker compose exec db psql -U webshop_user -d webshop_db

# Datenbank-Backup erstellen
docker compose exec db pg_dump -U webshop_user webshop_db > backup.sql

# Backup wiederherstellen
docker compose exec -T db psql -U webshop_user webshop_db < backup.sql
```

---

## 👥 Rollen und Berechtigungen (Optional)

**Hinweis:** Das Script `create_roles_and_permissions.py` ist für das **Django Admin-Panel**, nicht für den Webshop selbst. Der Webshop nutzt das `Customer`-Model mit Session-basierter Authentifizierung.

### Nur ausführen, wenn Admin-Berechtigungen benötigt werden:

1. **Django Shell im Docker starten:**
```bash
docker compose exec web python manage.py shell
```

2. **Script-Inhalt kopieren und ausführen:**

Öffne `create_roles_and_permissions.py` und kopiere die relevanten Abschnitte in die Shell.

**Erstellt:**
- 3 User: `tim`, `zoe`, `vincent` (Passwort: `1234`)
- 3 Gruppen: `Admins`, `Editors`, `Readers`
- Berechtigungen für Models

**Für Webshop-Kunden:** Registrierung über `/register` verwenden!

---

## 📊 Testdaten

Nach dem ersten Start sind folgende Daten vorhanden:

### Produkte
- Mehrere T-Shirts in verschiedenen Kategorien
- Preise zwischen 5€ und 50€
- Verschiedene Lagerbestände

### Kategorien
- Textilien
- Elektronik
- Bücher
- etc.

### Admin-Zugang
- Username: `admin`
- Passwort: `1234`

**Tipp:** Eigene Test-Kunden über `/register` anlegen!

---

## 🐛 Troubleshooting

### Problem: "Port 8000 already in use"

**Lösung:**
```bash
# Anderen Prozess finden und beenden (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Oder anderen Port verwenden
docker compose run -p 8001:8000 web
```

### Problem: "Database connection failed"

**Lösung:**
```bash
# Container neustarten
docker compose down
docker compose up -d db
# Warten 5 Sekunden
docker compose up web
```

### Problem: "No module named 'shop'"

**Lösung:**
```bash
# Im richtigen Verzeichnis?
cd webshop  # Wo manage.py liegt
python manage.py runserver
```

### Problem: "CRLF line ending error" (Linux/Mac)

**Lösung:**
```bash
# init.sh konvertieren
dos2unix init.sh
# Oder im Dockerfile bereits gefixt (sed-Befehl)
```

### Problem: Migrations fehlen

**Lösung:**
```bash
docker compose exec web python manage.py makemigrations shop
docker compose exec web python manage.py migrate
```

### Problem: Static Files werden nicht geladen

**Lösung:**
```bash
docker compose exec web python manage.py collectstatic --noinput
```

---

## 🔒 Sicherheit für Produktion

**⚠️ Vor Production-Deployment ändern:**

1. **SECRET_KEY** generieren:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

2. **DEBUG** auf `False` setzen in `.env`:
```env
DEBUG=0
```

3. **ALLOWED_HOSTS** konfigurieren in `settings.py`:
```python
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
```

4. **Passwörter ändern:**
- Admin-Passwort
- Datenbank-Passwort
- Alle Test-User

5. **HTTPS erzwingen** in `settings.py`:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## 📂 Projekt-Struktur

```
Challenge-III-Webshop/
├── webshop/                    # Django Projekt Root
│   ├── manage.py              # Django CLI
│   ├── requirements.txt       # Python Dependencies
│   ├── Dockerfile             # Container Image
│   ├── compose.yml            # Docker Compose Config
│   ├── init.sh                # Container Startup Script
│   ├── webshop/               # Django Projekt Config
│   │   ├── settings.py       # Django Settings
│   │   ├── urls.py           # Root URL Config
│   │   └── wsgi.py           # WSGI Entry Point
│   └── shop/                  # Hauptapplikation
│       ├── models.py         # Datenmodelle
│       ├── views.py          # View Functions
│       ├── views_cart.py     # Warenkorb & Checkout
│       ├── views_login.py    # Authentifizierung
│       ├── views_order.py    # Bestellungen
│       ├── urls.py           # URL Routing
│       ├── admin.py          # Admin-Panel Config
│       ├── templates/        # HTML Templates
│       ├── static/           # CSS, JS, Images
│       └── fixtures/         # Initial Data (YAML)
├── README.md                  # Projekt-Beschreibung
├── TECHNICAL_DOCUMENTATION.md # Technische Doku
└── SETUP.md                   # Diese Datei
```

---

## 🧪 Tests ausführen

```bash
# Alle Tests
docker compose exec web python manage.py test

# Spezifische App
docker compose exec web python manage.py test shop

# Mit Coverage
docker compose exec web coverage run --source='.' manage.py test
docker compose exec web coverage report
```

**Hinweis:** Aktuell noch keine Tests implementiert (steht in TODO).

---

## 📚 Weitere Ressourcen

- **Django Dokumentation:** https://docs.djangoproject.com/
- **Docker Dokumentation:** https://docs.docker.com/
- **PostgreSQL Dokumentation:** https://www.postgresql.org/docs/

---

## 🤝 Team & Support

Bei Fragen oder Problemen:
1. Issues im Repository erstellen
2. Technische Dokumentation lesen (`TECHNICAL_DOCUMENTATION.md`)
3. Docker Logs prüfen (`docker compose logs`)

---

## ✅ Checkliste: Erfolgreiches Setup

- [ ] Repository geklont
- [ ] Docker Desktop läuft
- [ ] `docker compose up --build` ausgeführt
- [ ] http://localhost:8000 erreichbar
- [ ] Admin-Panel funktioniert (http://localhost:8000/admin)
- [ ] Produkte werden angezeigt
- [ ] Registrierung funktioniert
- [ ] Warenkorb funktioniert
- [ ] Checkout funktioniert
- [ ] Bestellung wird angezeigt

**Alles grün? Glückwunsch! 🎉**

---

*Letzte Aktualisierung: 10. Dezember 2025*
