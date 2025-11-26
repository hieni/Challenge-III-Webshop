# Challenge-III-Webshop
Webshop mit PostgreSQL und Django Framework


Erstmal ins richtige Verzeichnis wechseln:
```
cd webshop
```

Folgende Befehle zum erstmaligen Hochfahren des Docker Containers:
```docker
docker compose build
```
installiert alle Python Requirements, etc. 

Zum Hochfahren des Containers mit der Datenbank und Django:
```docker
docker compose up
```
 --> erreichbar unter [localhost:8000](http://localhost:8000/)

Zum Erstellen eines admin-users:

```docker
python manage.py createsuperuser
```

Enter your desired username and press enter.

```docker
Username: admin
```

You will then be prompted for your desired email address:

```docker
Email address: admin@example.com
```

Konvertieren der Daten in SQL Anweisungen:
(WICHTIG: App muss vorher in settings.py unter INSTALLED_APPS hinzugefügt werden)

```docker
python manage.py makemigrations
```

SQL Anweisungen ausführen:

```docker
python manage.py migrate
```
