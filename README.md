# Challenge-III-Webshop

Ein Webshop-Datenbank-Projekt mit PostgreSQL.

## Datenbank-Schema

Das Projekt implementiert folgendes ER-Modell:

- **CUSTOMER**: Kundendaten (customer_id, first_name, last_name, email, password, strasse, ort, plz)
- **CATEGORY**: Produktkategorien (category_id, category_name)
- **PRODUCT**: Produkte (product_id, name, description, price, stock, category_id)
- **ORDER**: Bestellungen (order_id, customer_id, order_date, status, total_amount)
- **ORDER_ITEM**: Bestellpositionen (order_item_id, order_id, product_id, quantity, price_per_unit)
- **CART**: Warenkorb (cart_id, customer_id, last_updated)
- **CART_ITEM**: Warenkorb-Artikel (cart_item_id, cart_id, product_id, quantity)

## Setup

### Voraussetzungen
- Docker und Docker Desktop installiert
- PostgreSQL Client (optional, für direkte Datenbankverbindungen)

### Datenbank starten

1. Docker Desktop starten
2. Datenbank mit Docker Compose starten:
```powershell
docker-compose up -d
```

Die Datenbank wird automatisch initialisiert mit:
- Tabellen erstellen (`01_create_tables.sql`)
- Beispieldaten einfügen (`02_insert_sample_data.sql`)

### Verbindung zur Datenbank

**Verbindungsdetails:**
- Host: `localhost`
- Port: `5432`
- Datenbank: `webshop_db`
- Benutzer: `webshop_user`
- Passwort: `webshop_password`

**Connection String:**
```
postgresql://webshop_user:webshop_password@localhost:5432/webshop_db
```

## Dateien

- `01_create_tables.sql` - Erstellt alle Tabellen mit Beziehungen und Indexes
- `02_insert_sample_data.sql` - Fügt Beispieldaten ein
- `03_queries.sql` - Nützliche Abfragen für den Webshop
- `docker-compose.yml` - Docker-Konfiguration für PostgreSQL
- `.env.example` - Beispiel für Umgebungsvariablen

## Nützliche Docker-Befehle

```powershell
# Datenbank starten
docker-compose up -d

# Datenbank stoppen
docker-compose down

# Logs anzeigen
docker-compose logs -f

# In die PostgreSQL-Konsole verbinden
docker exec -it webshop_postgres psql -U webshop_user -d webshop_db

# Datenbank und Volumes löschen (Vorsicht: alle Daten werden gelöscht!)
docker-compose down -v
```

## Beispiel-Abfragen

Siehe `03_queries.sql` für verschiedene nützliche Abfragen:
- Alle Produkte mit Kategorien
- Bestellungen eines Kunden
- Warenkorb-Inhalte
- Bestseller-Produkte
- Produkte mit niedrigem Lagerbestand
- Kundenbestellhistorie
Webshop mit SQL-Datenbank und Vue/React
