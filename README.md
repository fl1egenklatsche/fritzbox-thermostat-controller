FritzBox Thermostat Controller

FastAPI app to monitor and control AVM FRITZ!DECT thermostats

Quickstart (development)

1) Build and run with docker-compose
   docker-compose up --build -d
   Visit http://localhost:9999

2) Environment
   - DATABASE_URL: sqlite+aiosqlite:///app/data/fritz_history.db
   - FRITZ_HOST/FRITZ_USER/FRITZ_PASS: TR-064 credentials (optional, placeholders in compose)
   - TELEGRAM_ALERTS: false by default

3) Mock mode
   If python-fritzconnection or a FRITZ!Box is not available the app uses a Mock adapter so UI and flows can be tested without hardware

Docker/Portainer
- Expose port 9999 and mount a volume for /app/data
- Provide TR-064 credentials via .env or Docker secrets when ready

Notes
- This is an initial feature branch implementation with Docker + UI + mock backend
- Next: implement full TR-064 DECT thermostat methods, persistent polling and alerts
