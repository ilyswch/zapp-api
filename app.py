import streamlink
import json
import requests
from flask import Flask, jsonify, redirect

app = Flask(__name__)

# Funktion zur Extraktion des Livestreams
def extract_stream_url(embedded_url):
    try:
        # Streamlink verwenden, um die Streams aufzulösen
        streams = streamlink.streams(embedded_url)
        if 'best' in streams:
            # M3U8-URL des besten Streams extrahieren
            stream_url = streams['best'].url
            return stream_url
        else:
            return None
    except Exception as e:
        print(f"Fehler beim Extrahieren des Streams: {e}")
        return None

@app.route('/stream/<channel>.m3u8')
def get_stream(channel):
    try:
        # Beispiel: Mapping der Channel-URLs (kann auch aus einer Datei oder Datenbank kommen)
        channels = {
            "channel1": "https://www.showturk.com.tr/canli-yayin/showturk",
            "channel2": "https://www.nowtv.com.tr/canli-yayin"
        }
        
        if channel in channels:
            embedded_url = channels[channel]
            
            # Livestream-URL extrahieren
            stream_url = extract_stream_url(embedded_url)
            
            if stream_url:
                # Benutzer auf den extrahierten Stream weiterleiten
                return redirect(stream_url)
            else:
                return jsonify({"error": "Kein Stream gefunden"}), 404
        else:
            return jsonify({"error": "Channel nicht gefunden"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
