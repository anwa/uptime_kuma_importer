# Uptime Kuma Importer

## Setup

1. Repository clonen:

```bash
git clone https://github.com/anwa/uptime_kuma_importer.git
cd uptime_kuma_importer
```

2. Virtuelle Umgebung erstellen und aktivieren:

```bash
py -m venv venv
.\venv\Scripts\activate
```

3. Bibliotheken installieren:

```bash
pip install -r requirements.txt
```

4. Anwendung starten:

```bash
py import.py
```
## Pflege der Requirements

**Achtung:** Alle Befehle müssen in der aktivierten virtuellen Umgebung gemacht werden!

1. Alle installierten Pakete auflisten:

```bash
pip freeze
```

2. Veraltete (outdated) Python-Pakete in deiner aktuellen Umgebung anzuzeigen

```bash
pip list --outdated
```

3. Ein bestimmtes Paket aktualisieren

```bash
pip install --upgrade paketname
```

4. Alle Pakete auf die neuesten Versionen updaten

```bash
pip install --upgrade -r requirements.txt
```
