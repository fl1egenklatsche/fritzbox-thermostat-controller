# FritzBox Thermostat Controller

Web tool to monitor and control AVM FRITZ!DECT thermostats registered to a FRITZ!Box

Features
- Discover FRITZ!DECT thermostats via TR-064
- Live telemetry: temperature, battery, valve position, signal strength
- Control: set target temperature, mode (auto/manual), boost
- Historical logging (SQLite) and simple charts
- Runs as a FastAPI service, optional Docker

Note
- Configure FRITZ!Box credentials locally
- You run the configuration/setup on the FRITZ!Box network; the tool can run on a remote server

License: MIT
