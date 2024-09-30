from flask import Flask, jsonify, redirect
import requests
from bs4 import BeautifulSoup
import time
import json

app = Flask(__name__)

# Beispiel wie du die Konfigurationsdatei laden könntest
with open("config.json", "r") as f:
    channel_urls = json.load(f)["channels"]

# Caching-Objekt, das die letzten Abrufe speichert
cache = {}

# Fallback-URL für offline Channels
FALLBACK_URL = "https://fallback.de/fallbackvideo.mp4"

# Cache Timeout (in Sekunden, hier 3600 = 1 Stunde)
CACHE_TIMEOUT = 3600

def get_stream_url(channel_url):
    """Extrahiert die m3u8 URL von der angegebenen Webseite"""
    try:
        response = requests.get(channel_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Annahme: Die m3u8-URL ist in einem <source> Tag eingebettet
        stream_element = soup.find("source", {"type": "application/vnd.apple.mpegurl"})
        if stream_element:
            return stream_element["src"]
        return None
    except Exception as e:
        print(f"Fehler beim Abrufen der Stream-URL: {e}")
        return None

@app.route("/stream/<channel>.m3u")
def stream(channel):
    # Prüfen, ob der Channel in der Konfiguration existiert
    if channel not in channel_urls:
        return jsonify({"error": "Channel not found"}), 404

    current_time = time.time()

    # Prüfen, ob der Channel gecached ist und ob der Cache noch gültig ist
    if channel in cache:
        cached_data = cache[channel]
        if current_time - cached_data["timestamp"] < CACHE_TIMEOUT:
            # Verwende den gecachten Link, wenn der Cache noch gültig ist
            return redirect(cached_data["url"])

    # URL der Seite des Kanals
    channel_url = channel_urls[channel]
    
    # m3u8-Stream-URL extrahieren
    stream_url = get_stream_url(channel_url)
    
    if stream_url:
        # Update den Cache mit der neuen URL und dem Timestamp
        cache[channel] = {
            "url": stream_url,
            "timestamp": current_time
        }
        return redirect(stream_url)
    else:
        # Falls keine URL gefunden wird, verwende die Fallback-URL
        cache[channel] = {
            "url": FALLBACK_URL,
            "timestamp": current_time
        }
        return redirect(FALLBACK_URL)

if __name__ == "__main__":
    app.run(debug=True)
