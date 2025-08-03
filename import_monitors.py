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
        # Tag existiert nicht, erstelle einen neuen
        logging.info(f"Erstelle neuen Tag: {tag_name} mit Farbe {tag_color}")
        tag_result = api.add_tag(name=tag_name, color=tag_color)
        logging.debug(f"API-Antwort für Tag-Erstellung: {tag_result}")
        tag_id = tag_result.get('id')
        if tag_id is None:
            logging.error(f"Tag '{tag_name}' konnte nicht erstellt werden: tag_id ist None")
            # Workaround: Suche den Tag erneut in der Liste
            existing_tags = api.get_tags()
            for tag in existing_tags:
                if tag['name'] == tag_name:
                    logging.info(f"Tag '{tag_name}' nach erneuter Suche gefunden (ID: {tag['id']})")
                    return tag['id']
            logging.error(f"Tag '{tag_name}' konnte nicht gefunden oder erstellt werden.")
            return None
        logging.info(f"Tag '{tag_name}' erstellt (ID: {tag_id})")
        return tag_id
    except Exception as e:
        logging.error(f"Fehler beim Abrufen oder Erstellen des Tags '{tag_name}': {e}")
        return None

def add_monitor(api, monitor_config):
    """Füge einen Monitor hinzu."""
    try:
        # Entferne tags aus der Konfiguration, da sie separat behandelt werden
        tags = monitor_config.pop('tags', [])
        logging.info(f"Erstelle Monitor: {monitor_config['name']}")
        result = api.add_monitor(**monitor_config)
        monitor_id = result.get('monitorID')
        logging.info(f"Monitor '{monitor_config['name']}' erfolgreich hinzugefügt (ID: {monitor_id})")

        # Tags hinzufügen
        for tag in tags:
            tag_name = tag['name']
            tag_color = tag.get('color', '#000000')  # Standardfarbe, falls nicht angegeben
            tag_id = get_or_create_tag(api, tag_name, tag_color)
            if tag_id:
                try:
                    logging.info(f"Verknüpfe Tag '{tag_name}' mit Monitor ID {monitor_id}")
                    api.add_monitor_tag(tag_id=tag_id, monitor_id=monitor_id)
                    logging.info(f"Tag '{tag_name}' mit Monitor '{monitor_config['name']}' verknüpft")
                except Exception as e:
                    logging.error(f"Fehler beim Verknüpfen des Tags '{tag_name}' mit Monitor '{monitor_config['name']}': {e}")
            else:
                logging.warning(f"Tag '{tag_name}' konnte nicht erstellt oder gefunden werden.")
        return result
    except Exception as e:
        logging.error(f"Fehler beim Hinzufügen des Monitors '{monitor_config.get('name', 'Unbekannt')}': {e}")
        return None

def main():
    """Hauptfunktion zum Importieren von Monitoren."""
    try:
        # Lade die Konfigurationsdatei
        monitors = load_config(INPUT_FILE)

        # Verbinde mit Uptime Kuma
        with UptimeKumaApi(API_URL) as api:
            logging.info("Verbinde mit Uptime Kuma API")
            api.login(USERNAME, PASSWORD)
            logging.info("Erfolgreich eingeloggt")
            
            # Füge jeden Monitor hinzu
            for monitor in monitors:
                add_monitor(api, monitor)
                
        logging.info("Alle Monitore erfolgreich importiert.")
    except Exception as e:
        logging.error(f"Fehler: {e}")

if __name__ == "__main__":
    main()