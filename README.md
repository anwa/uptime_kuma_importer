# HA

## Setup

1. Repository clonen:

```bash
git clone https://github.com/anwa/ha.git
cd HA
```

2. Virtuelle Umgebung erstellen und aktivieren:

```bash
python -m venv venv
source venv/bin/activate  # Linux
.\venv\Scripts\activate   # Windows   
```

3. Bibliotheken installieren:

```bash
pip install -r requirements.txt
```

4. Anwendung starten:

```bash
python replace_unique_id.py
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
pip install --upgrade -r requirements-linux.txt    # Linux
pip install --upgrade -r requirements-windows.txt  # Windows
```
