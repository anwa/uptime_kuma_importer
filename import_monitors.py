import json
import yaml
from uptime_kuma_api import UptimeKumaApi, MonitorType

# Konfiguration
API_URL = "http://10.10.1.30:3010"  # Ersetze mit deiner Uptime Kuma URL
USERNAME = "andreas"  # Ersetze mit deinem Benutzernamen
PASSWORD = "NnwUodU4K6wa934HfvsFA7GQsDMsdW8A"  # Ersetze mit deinem Passwort
INPUT_FILE = "monitors.yaml"  # Oder "monitors.json"

def load_config(file_path):
    """Lade die Konfigurationsdatei (JSON oder YAML)."""
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
        existing_tags = api.get_tags()
        for tag in existing_tags:
            if tag['name'] == tag_name:
                print(f"Tag '{tag_name}' existiert bereits (ID: {tag['id']})")
                return tag['id']
        # Tag existiert nicht, erstelle einen neuen
        tag_result = api.add_tag(name=tag_name, color=tag_color)
        tag_id = tag_result.get('tag_id')
        print(f"Tag '{tag_name}' erstellt (ID: {tag_id})")
        return tag_id
    except Exception as e:
        print(f"Fehler beim Abrufen oder Erstellen des Tags '{tag_name}': {e}")
        return None

def add_monitor(api, monitor_config):
    """Füge einen Monitor hinzu."""
    try:
        # Entferne tags aus der Konfiguration, da sie separat behandelt werden
        tags = monitor_config.pop('tags', [])
        result = api.add_monitor(**monitor_config)
        monitor_id = result.get('monitorID')
        print(f"Monitor '{monitor_config['name']}' erfolgreich hinzugefügt (ID: {monitor_id})")

        # Tags hinzufügen
        for tag in tags:
            tag_name = tag['name']
            tag_color = tag.get('color', '#000000')  # Standardfarbe, falls nicht angegeben
            tag_id = get_or_create_tag(api, tag_name, tag_color)
            if tag_id:
                try:
                    api.add_monitor_tag(tag_id=tag_id, monitor_id=monitor_id, value=None)
                    print(f"Tag '{tag_name}' mit Monitor '{monitor_config['name']}' verknüpft")
                except Exception as e:
                    print(f"Fehler beim Verknüpfen des Tags '{tag_name}' mit Monitor '{monitor_config['name']}': {e}")
            else:
                print(f"Tag '{tag_name}' konnte nicht erstellt oder gefunden werden.")
        return result
    except Exception as e:
        print(f"Fehler beim Hinzufügen des Monitors '{monitor_config.get('name', 'Unbekannt')}': {e}")
        return None

def main():
    """Hauptfunktion zum Importieren von Monitoren."""
    try:
        # Lade die Konfigurationsdatei
        monitors = load_config(INPUT_FILE)

        # Verbinde mit Uptime Kuma
        with UptimeKumaApi(API_URL) as api:
            api.login(USERNAME, PASSWORD)
            
            # Füge jeden Monitor hinzu
            for monitor in monitors:
                add_monitor(api, monitor)
                
        print("Alle Monitore erfolgreich importiert.")
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    main()    