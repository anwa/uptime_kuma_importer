import json
import yaml
import logging
from uptime_kuma_api import UptimeKumaApi, MonitorType

# Logging-Konfiguration für detaillierte Fehlersuche
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Konfiguration
API_URL = "http://10.10.1.30:3010"  # Ersetze mit deiner Uptime Kuma URL
USERNAME = "andreas"  # Ersetze mit deinem Benutzernamen
PASSWORD = "NnwUodU4K6wa934HfvsFA7GQsDMsdW8A"  # Ersetze mit deinem Passwort
INPUT_FILE = "monitors.yaml"  # Oder "monitors.json"

def load_config(file_path):
    """Lade die Konfigurationsdatei (JSON oder YAML)."""
    logging.info(f"Lade Konfigurationsdatei: {file_path}")
    with open(file_path, 'r') as file:
        if file_path.endswith('.json'):
            return json.load(file)
        elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
            return yaml.safe_load(file)['monitors']
        else:
            raise ValueError("Unsupported file format. Use JSON or YAML.")

def monitor_exists(api, monitor_name):
    """Prüfe, ob ein Monitor oder eine Gruppe mit dem angegebenen Namen existiert."""
    try:
        existing_monitors = api.get_monitors()
        for monitor in existing_monitors:
            if monitor['name'] == monitor_name:
                logging.info(f"Monitor/Gruppe '{monitor_name}' existiert bereits (ID: {monitor['id']})")
                return monitor['id']
        logging.info(f"Monitor/Gruppe '{monitor_name}' existiert nicht")
        return None
    except Exception as e:
        logging.error(f"Fehler beim Abrufen der Monitore: {e}")
        return None

def get_or_create_tag(api, tag_name, tag_color):
    """Prüfe, ob ein Tag existiert, und erstelle ihn ggf."""
    try:
        logging.info(f"Prüfe Tag: {tag_name}")
        existing_tags = api.get_tags()
        logging.debug(f"Bestehende Tags: {existing_tags}")
        for tag in existing_tags:
            if tag['name'] == tag_name:
                logging.info(f"Tag '{tag_name}' existiert bereits (ID: {tag['id']})")
                return tag['id']
        
        logging.info(f"Erstelle neuen Tag: {tag_name} mit Farbe {tag_color}")
        tag_result = api.add_tag(name=tag_name, color=tag_color)
        logging.debug(f"API-Antwort für Tag-Erstellung: {tag_result}")
        tag_id = tag_result.get('id')
        if not tag_id:
            logging.error(f"Tag '{tag_name}' konnte nicht erstellt werden: Keine ID in Antwort")
            return None
        logging.info(f"Tag '{tag_name}' erstellt (ID: {tag_id})")
        return tag_id
    except Exception as e:
        logging.error(f"Fehler beim Abrufen oder Erstellen des Tags '{tag_name}': {e}")
        return None

def add_monitor_tag(api, tag_id, monitor_id):
    """Verknüpfe einen Tag mit einem Monitor."""
    try:
        logging.info(f"Verknüpfe Tag ID {tag_id} mit Monitor ID {monitor_id}")
        api.add_monitor_tag(tag_id=tag_id, monitor_id=monitor_id)  # value="" als Default
        logging.info(f"Tag ID {tag_id} erfolgreich mit Monitor ID {monitor_id} verknüpft")
    except Exception as e:
        logging.error(f"Fehler beim Verknüpfen des Tags ID {tag_id} mit Monitor ID {monitor_id}: {e}")

def add_monitor(api, monitor_config):
    """Füge einen Monitor oder eine Gruppe hinzu, falls sie nicht existiert."""
    try:
        monitor_name = monitor_config['name']
        # Prüfe, ob der Monitor/Gruppe bereits existiert
        monitor_id = monitor_exists(api, monitor_name)
        if monitor_id:
            logging.info(f"Monitor/Gruppe '{monitor_name}' wird übersprungen, da sie bereits existiert")
        else:
            # Prüfe, ob die übergeordnete Gruppe existiert (falls parent angegeben)
            parent_name = monitor_config.get('parent')
            parent_id = None
            if parent_name:
                parent_id = monitor_exists(api, parent_name)
                if not parent_id:
                    logging.error(f"Übergeordnete Gruppe '{parent_name}' existiert nicht. Monitor/Gruppe '{monitor_name}' wird nicht erstellt.")
                    return None
                logging.info(f"Übergeordnete Gruppe '{parent_name}' gefunden (ID: {parent_id})")
                monitor_config['parent'] = parent_id  # Setze die parent-ID für die API

            # Monitor oder Gruppe erstellen
            logging.info(f"Erstelle Monitor/Gruppe: {monitor_name}")
            tags = monitor_config.pop('tags', [])  # Entferne Tags temporär
            result = api.add_monitor(**monitor_config)
            monitor_id = result.get('monitorID')
            logging.info(f"Monitor/Gruppe '{monitor_name}' erfolgreich hinzugefügt (ID: {monitor_id})")

            # Tags hinzufügen (falls vorhanden)
            for tag in tags:
                tag_name = tag['name']
                tag_color = tag.get('color', '#000000')  # Standardfarbe
                tag_id = get_or_create_tag(api, tag_name, tag_color)
                if tag_id:
                    # Prüfe, ob der Tag bereits verknüpft ist
                    existing_monitor_tags = api.get_monitor(monitor_id).get('tags', [])
                    if not any(t['id'] == tag_id for t in existing_monitor_tags):
                        add_monitor_tag(api, tag_id, monitor_id)
                    else:
                        logging.info(f"Tag '{tag_name}' bereits mit Monitor/Gruppe '{monitor_name}' verknüpft")
                else:
                    logging.warning(f"Tag '{tag_name}' konnte nicht erstellt oder gefunden werden")

        return {'monitorID': monitor_id}
    except Exception as e:
        logging.error(f"Fehler beim Hinzufügen des Monitors/Gruppe '{monitor_config.get('name', 'Unbekannt')}': {e}")
        return None

def main():
    """Hauptfunktion zum Importieren von Monitoren und Gruppen."""
    try:
        # Lade die Konfigurationsdatei
        monitors = load_config(INPUT_FILE)

        # Verbinde mit Uptime Kuma
        with UptimeKumaApi(API_URL) as api:
            logging.info("Verbinde mit Uptime Kuma API")
            api.login(USERNAME, PASSWORD)
            logging.info("Erfolgreich eingeloggt")
            
            # Füge jeden Monitor oder jede Gruppe hinzu
            for monitor in monitors:
                add_monitor(api, monitor)
                
        logging.info("Alle Monitore und Gruppen erfolgreich importiert.")
    except Exception as e:
        logging.error(f"Fehler: {e}")

if __name__ == "__main__":
    main()