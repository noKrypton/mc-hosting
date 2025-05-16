    </div>

    <!-- Vue.js und Axios -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vue/3.2.36/vue.global.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/axios/0.21.1/axios.min.js"></script>
    
    <script>
        const { createApp, ref, onMounted, computed } = Vue;
        
        const app = createApp({
            setup() {
                // Auth State
                const isAuthenticated = ref(false);
                const token = ref('');
                const loginForm = ref({
                    username: '',
                    password: ''
                });
                
                // App State
                const activePage = ref('dashboard');
                const servers = ref([]);
                const systemStats = ref({
                    cpu: { percent: 0, cores: 0 },
                    memory: { total: 0, available: 0, percent: 0 },
                    disk: { total: 0, used: 0, free: 0, percent: 0 },
                    network: { bytes_sent: 0, bytes_recv: 0 },
                    timestamp: null
                });
                const settings = ref({
                    serverDir: '~/minecraft_servers',
                    defaultRam: 1024,
                    backupInterval: 'none'
                });
                
                // Modal States
                const showNewServerModal = ref(false);
                const showConsoleModal = ref(false);
                const showServerSettingsModal = ref(false);
                const showDeleteConfirmModal = ref(false);
                
                // Form Data
                const newServer = ref({
                    name: '',
                    version: '1.19.4',
                    port: 25565,
                    ram: 1024
                });
                
                // Selected Server and Console
                const selectedServer = ref(null);
                const serverLogs = ref([]);
                const consoleCommand = ref('');
                const serverProperties = ref({});
                
                // Fetch System Stats
                const fetchSystemStats = async () => {
                    try {
                        const response = await axios.get('/api/system/stats', {
                            headers: { 'Authorization': `Bearer ${token.value}` }
                        });
                        systemStats.value = response.data;
                    } catch (error) {
                        console.error('Fehler beim Abrufen der Systemstatistiken:', error);
                    }
                };
                
                // Fetch Servers
                const fetchServers = async () => {
                    try {
                        const response = await axios.get('/api/servers', {
                            headers: { 'Authorization': `Bearer ${token.value}` }
                        });
                        servers.value = response.data;
                    } catch (error) {
                        console.error('Fehler beim Abrufen der Server:', error);
                    }
                };
                
                // Login Function
                const login = async () => {
                    try {
                        const response = await axios.post('/api/auth', loginForm.value);
                        token.value = response.data.access_token;
                        localStorage.setItem('token', token.value);
                        isAuthenticated.value = true;
                        
                        // Nach erfolgreicher Anmeldung Daten laden
                        await fetchServers();
                        await fetchSystemStats();
                        
                        // Regelmäßige Updates
                        setInterval(fetchSystemStats, 5000);
                        setInterval(fetchServers, 10000);
                    } catch (error) {
                        alert('Anmeldung fehlgeschlagen. Bitte überprüfe deine Zugangsdaten.');
                        console.error('Login error:', error);
                    }
                };
                
                // Logout Function
                const logout = () => {
                    token.value = '';
                    localStorage.removeItem('token');
                    isAuthenticated.value = false;
                };
                
                // Change Active Page
                const setActivePage = (page) => {
                    activePage.value = page;
                };
                
                // Format Bytes Utility
                const formatBytes = (bytes, decimals = 2) => {
                    if (bytes === 0) return '0 Bytes';
                    
                    const k = 1024;
                    const dm = decimals < 0 ? 0 : decimals;
                    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
                    
                    const i = Math.floor(Math.log(bytes) / Math.log(k));
                    
                    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
                };
                
                // Server Functions
                const createServer = async () => {
                    try {
                        const response = await axios.post('/api/servers', newServer.value, {
                            headers: { 'Authorization': `Bearer ${token.value}` }
                        });
                        
                        alert(`Server ${newServer.value.name} wurde erstellt!`);
                        showNewServerModal.value = false;
                        
                        // Server-Liste aktualisieren
                        await fetchServers();
                        
                        // Form zurücksetzen
                        newServer.value = {
                            name: '',
                            version: '1.19.4',
                            port: 25565,
                            ram: 1024
                        };
                    } catch (error) {
                        alert('Fehler beim Erstellen des Servers: ' + error.response?.data?.error || error.message);
                        console.error('Server creation error:', error);
                    }
                };
                
                const startServer = async (server) => {
                    try {
                        await axios.post(`/api/servers/${server.name}/start`, {}, {
                            headers: { 'Authorization': `Bearer ${token.value}` }
                        });
                        
                        alert(`Server ${server.name} wird gestartet!`);
                        
                        // Server-Liste aktualisieren
                        setTimeout(fetchServers, 2000);
                    } catch (error) {
                        alert('Fehler beim Starten des Servers: ' + error.response?.data?.error || error.message);
                        console.error('Server start error:', error);
                    }
                };
                
                const stopServer = async (server) => {
                    try {
                        await axios.post(`/api/servers/${server.name}/stop`, {}, {
                            headers: { 'Authorization': `Bearer ${token.value}` }
                        });
                        
                        alert(`Server ${server.name} wird gestoppt!`);
                        
                        // Server-Liste aktualisieren
                        setTimeout(fetchServers, 2000);
                    } catch (error) {
                        alert('Fehler beim Stoppen des Servers: ' + error.response?.data?.error || error.message);
                        console.error('Server stop error:', error);
                    }
                };
                
                const deleteServer = async () => {
                    if (!selectedServer.value) return;
                    
                    try {
                        await axios.delete(`/api/servers/${selectedServer.value.name}`, {
                            headers: { 'Authorization': `Bearer ${token.value}` }
                        });
                        
                        alert(`Server ${selectedServer.value.name} wurde gelöscht!`);
                        showDeleteConfirmModal.value = false;
                        
                        // Server-Liste aktualisieren
                        await fetchServers();
                    } catch (error) {
                        alert('Fehler beim Löschen des Servers: ' + error.response?.data?.error || error.message);
                        console.error('Server deletion error:', error);
                    }
                };
                
                const confirmDeleteServer = (server) => {
                    selectedServer.value = server;
                    showDeleteConfirmModal.value = true;
                };
                
                // Console Functions
                const openServerConsole = async (server) => {
                    selectedServer.value = server;
                    showConsoleModal.value = true;
                    await refreshLogs();
                };
                
                const refreshLogs = async () => {
                    if (!selectedServer.value) return;
                    
                    try {
                        const response = await axios.get(`/api/servers/${selectedServer.value.name}/logs`, {
                            headers: { 'Authorization': `Bearer ${token.value}` }
                        });
                        
                        // Logs in ein Array aufteilen
                        serverLogs.value = response.data.logs.split('\n');
                    } catch (error) {
                        console.error('Error fetching logs:', error);
                        serverLogs.value = ['Fehler beim Abrufen der Logs.'];
                    }
                };
                
                const sendCommand = async () => {
                    if (!selectedServer.value || !consoleCommand.value) return;
                    
                    try {
                        await axios.post(`/api/servers/${selectedServer.value.name}/command`, {
                            command: consoleCommand.value
                        }, {
                            headers: { 'Authorization': `Bearer ${token.value}` }
                        });
                        
                        // Befehl zum Log hinzufügen
                        serverLogs.value.push(`> ${consoleCommand.value}`);
                        
                        // Befehlsfeld zurücksetzen
                        consoleCommand.value = '';
                        
                        // Logs nach kurzer Pause aktualisieren, um die Ausgabe zu sehen
                        setTimeout(refreshLogs, 1000);
                    } catch (error) {
                        console.error('Error sending command:', error);
                        serverLogs.value.push('Fehler beim Senden des Befehls.');
                    }
                };
                
                // Server Settings Functions
                const openServerSettings = async (server) => {
                    selectedServer.value = server;
                    
                    try {
                        const response = await axios.get(`/api/servers/${server.name}/properties`, {
                            headers: { 'Authorization': `Bearer ${token.value}` }
                        });
                        
                        serverProperties.value = response.data.properties;
                        showServerSettingsModal.value = true;
                    } catch (error) {
                        console.error('Error fetching server properties:', error);
                        alert('Fehler beim Abrufen der Servereinstellungen.');
                    }
                };
                
                const saveServerSettings = async () => {
                    if (!selectedServer.value) return;
                    
                    try {
                        await axios.put(`/api/servers/${selectedServer.value.name}/properties`, {
                            properties: serverProperties.value
                        }, {
                            headers: { 'Authorization': `Bearer ${token.value}` }
                        });
                        
                        alert('Servereinstellungen gespeichert!');
                        showServerSettingsModal.value = false;
                        
                        // Server-Liste aktualisieren
                        await fetchServers();
                    } catch (error) {
                        console.error('Error saving server properties:', error);
                        alert('Fehler beim Speichern der Servereinstellungen.');
                    }
                };
                
                // App Settings Functions
                const saveSettings = () => {
                    alert('Einstellungen gespeichert!');
                    // In einer Produktionsumgebung würden die Einstellungen an einen API-Endpunkt gesendet
                };
                
                // Helper Functions
                const getOnlineServersCount = () => {
                    return servers.value.filter(server => server.running).length;
                };
                
                const getRunningServers = () => {
                    return servers.value.filter(server => server.running);
                };
                
                // Check if user is already logged in
                onMounted(() => {
                    const savedToken = localStorage.getItem('token');
                    if (savedToken) {
                        token.value = savedToken;
                        isAuthent"""
CraftForge - Futuristisches Minecraft Server Hosting Panel
======================================================

Technologie-Stack:
- Backend: Sanic (Python Web Framework für hohe Performance)
- Frontend: HTML5, CSS3, JavaScript mit Vue.js
- Datenbank: SQLite für lokale Entwicklung, PostgreSQL für Produktion
- Authentifizierung: JWT (JSON Web Tokens)
- Minecraft Server Management: RCON-Protokoll und Shell-Befehle

Struktur:
1. Backend (Sanic API)
2. Frontend (Vue.js SPA)
3. Minecraft Server Manager (Python-Modul)
"""

# Hauptkomponenten

## 1. Backend-Code (app.py)

```python
from sanic import Sanic, response
from sanic_cors import CORS
from sanic_jwt import Initialize, protected
import os
import json
import subprocess
import asyncio
import psutil
from datetime import datetime

# Anwendung initialisieren
app = Sanic("CraftForge")
CORS(app)

# Konfiguration
app.config.MINECRAFT_SERVERS_DIR = os.path.expanduser("~/minecraft_servers")
os.makedirs(app.config.MINECRAFT_SERVERS_DIR, exist_ok=True)

# Benutzerauth (für Produktionsumgebung sollte diese in einer Datenbank gespeichert werden)
USERS = {
    "admin": {
        "username": "admin",
        "password": "adminpassword",  # In Produktion: gehashtes Passwort
        "role": "admin"
    }
}

# JWT-Authentifizierung konfigurieren
async def authenticate(request, *args, **kwargs):
    username = request.json.get("username", "")
    password = request.json.get("password", "")
    
    user = USERS.get(username)
    
    if user and user["password"] == password:
        return user
    
    return None

Initialize(app, authenticate=authenticate)

# Server-Daten-Manager
async def get_servers_data():
    servers_data = []
    
    for server_name in os.listdir(app.config.MINECRAFT_SERVERS_DIR):
        server_path = os.path.join(app.config.MINECRAFT_SERVERS_DIR, server_name)
        if os.path.isdir(server_path):
            # Server-Konfiguration laden
            properties_path = os.path.join(server_path, "server.properties")
            properties = {}
            if os.path.exists(properties_path):
                with open(properties_path, "r") as f:
                    for line in f.readlines():
                        if line.strip() and not line.startswith("#"):
                            key, value = line.strip().split("=", 1)
                            properties[key] = value
            
            # Server-Status überprüfen
            is_running = False
            for process in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'java' in process.info['name'] and server_name in ' '.join(process.info.get('cmdline', [])):
                    is_running = True
                    break
            
            # Server-Info sammeln
            server_info = {
                "name": server_name,
                "path": server_path,
                "properties": properties,
                "running": is_running,
                "port": properties.get("server-port", "25565"),
                "version": "Unknown",  # In einer erweiterten Version könnte die Version aus der JAR-Datei extrahiert werden
                "last_start": None  # In einer erweiterten Version könnten Logs analysiert werden
            }
            
            servers_data.append(server_info)
    
    return servers_data

# Routen definieren

@app.route("/api/servers", methods=["GET"])
@protected()
async def list_servers(request):
    servers = await get_servers_data()
    return response.json(servers)

@app.route("/api/servers", methods=["POST"])
@protected()
async def create_server(request):
    data = request.json
    
    if not data or "name" not in data:
        return response.json({"error": "Server name is required"}, status=400)
    
    server_name = data["name"]
    version = data.get("version", "1.19.2")  # Standardversion
    ram = data.get("ram", 1024)  # RAM in MB
    port = data.get("port", 25565)
    
    # Neues Serververzeichnis erstellen
    server_path = os.path.join(app.config.MINECRAFT_SERVERS_DIR, server_name)
    if os.path.exists(server_path):
        return response.json({"error": "Server already exists"}, status=400)
    
    os.makedirs(server_path)
    
    # Server-JAR herunterladen (hier vereinfacht dargestellt)
    download_cmd = f"cd {server_path} && wget https://launcher.mojang.com/v1/objects/125e5adf40c659fd3bce3e66e67a16bb49ecc1b9/server.jar"
    await asyncio.create_subprocess_shell(download_cmd)
    
    # EULA akzeptieren
    with open(os.path.join(server_path, "eula.txt"), "w") as f:
        f.write("eula=true\n")
    
    # Server-Properties erstellen
    with open(os.path.join(server_path, "server.properties"), "w") as f:
        f.write(f"server-port={port}\n")
        f.write("gamemode=survival\n")
        f.write("difficulty=normal\n")
        f.write("spawn-protection=16\n")
        f.write("max-players=20\n")
        f.write("enable-command-block=false\n")
        f.write("enable-rcon=true\n")
        f.write("rcon.password=craftforge123\n")  # In der Produktion sollte ein sicheres Passwort verwendet werden
        f.write("rcon.port=25575\n")
    
    # Startskript erstellen
    with open(os.path.join(server_path, "start.sh"), "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"cd {server_path}\n")
        f.write(f"java -Xmx{ram}M -Xms{ram}M -jar server.jar nogui\n")
    
    # Skript ausführbar machen
    os.chmod(os.path.join(server_path, "start.sh"), 0o755)
    
    return response.json({"message": "Server created successfully", "server_name": server_name})

@app.route("/api/servers/<server_name>/start", methods=["POST"])
@protected()
async def start_server(request, server_name):
    server_path = os.path.join(app.config.MINECRAFT_SERVERS_DIR, server_name)
    if not os.path.exists(server_path):
        return response.json({"error": "Server not found"}, status=404)
    
    # Überprüfen, ob der Server bereits läuft
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'java' in process.info['name'] and server_name in ' '.join(process.info.get('cmdline', [])):
            return response.json({"error": "Server is already running"}, status=400)
    
    # Server starten
    start_cmd = f"cd {server_path} && nohup ./start.sh > server.log 2>&1 &"
    process = await asyncio.create_subprocess_shell(start_cmd)
    await process.communicate()
    
    return response.json({"message": f"Server {server_name} started"})

@app.route("/api/servers/<server_name>/stop", methods=["POST"])
@protected()
async def stop_server(request, server_name):
    server_running = False
    server_pid = None
    
    # Server-Prozess finden
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'java' in process.info['name'] and server_name in ' '.join(process.info.get('cmdline', [])):
            server_running = True
            server_pid = process.info['pid']
            break
    
    if not server_running:
        return response.json({"error": "Server is not running"}, status=400)
    
    # Server stoppen (SIGTERM senden)
    try:
        os.kill(server_pid, 15)  # SIGTERM
        return response.json({"message": f"Server {server_name} stopping"})
    except OSError:
        return response.json({"error": "Failed to stop the server"}, status=500)

@app.route("/api/servers/<server_name>/command", methods=["POST"])
@protected()
async def run_command(request, server_name):
    data = request.json
    
    if not data or "command" not in data:
        return response.json({"error": "Command is required"}, status=400)
    
    command = data["command"]
    
    # In einer Produktionsumgebung sollte hier RCON verwendet werden
    # Dies ist eine vereinfachte Darstellung für das Konzept
    return response.json({"message": f"Command '{command}' executed on server {server_name}"})

@app.route("/api/servers/<server_name>/logs", methods=["GET"])
@protected()
async def get_logs(request, server_name):
    server_path = os.path.join(app.config.MINECRAFT_SERVERS_DIR, server_name)
    if not os.path.exists(server_path):
        return response.json({"error": "Server not found"}, status=404)
    
    log_path = os.path.join(server_path, "server.log")
    if not os.path.exists(log_path):
        return response.json({"logs": ""})
    
    # Die letzten 100 Zeilen des Logs lesen
    lines = 100
    try:
        lines = int(request.args.get("lines", 100))
    except ValueError:
        pass
    
    try:
        result = subprocess.run(["tail", "-n", str(lines), log_path], capture_output=True, text=True)
        logs = result.stdout
        return response.json({"logs": logs})
    except Exception as e:
        return response.json({"error": f"Failed to read logs: {str(e)}"}, status=500)

@app.route("/api/servers/<server_name>/properties", methods=["GET"])
@protected()
async def get_properties(request, server_name):
    server_path = os.path.join(app.config.MINECRAFT_SERVERS_DIR, server_name)
    if not os.path.exists(server_path):
        return response.json({"error": "Server not found"}, status=404)
    
    properties_path = os.path.join(server_path, "server.properties")
    if not os.path.exists(properties_path):
        return response.json({"properties": {}})
    
    properties = {}
    with open(properties_path, "r") as f:
        for line in f.readlines():
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                properties[key] = value
    
    return response.json({"properties": properties})

@app.route("/api/servers/<server_name>/properties", methods=["PUT"])
@protected()
async def update_properties(request, server_name):
    data = request.json
    
    if not data or "properties" not in data:
        return response.json({"error": "Properties are required"}, status=400)
    
    server_path = os.path.join(app.config.MINECRAFT_SERVERS_DIR, server_name)
    if not os.path.exists(server_path):
        return response.json({"error": "Server not found"}, status=404)
    
    properties_path = os.path.join(server_path, "server.properties")
    
    # Aktuelle Properties laden
    current_properties = {}
    if os.path.exists(properties_path):
        with open(properties_path, "r") as f:
            for line in f.readlines():
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    current_properties[key] = value
    
    # Properties aktualisieren
    current_properties.update(data["properties"])
    
    # Properties speichern
    with open(properties_path, "w") as f:
        for key, value in current_properties.items():
            f.write(f"{key}={value}\n")
    
    return response.json({"message": "Properties updated successfully"})

@app.route("/api/servers/<server_name>", methods=["DELETE"])
@protected()
async def delete_server(request, server_name):
    server_path = os.path.join(app.config.MINECRAFT_SERVERS_DIR, server_name)
    if not os.path.exists(server_path):
        return response.json({"error": "Server not found"}, status=404)
    
    # Überprüfen, ob der Server läuft
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'java' in process.info['name'] and server_name in ' '.join(process.info.get('cmdline', [])):
            return response.json({"error": "Server is running. Please stop it first."}, status=400)
    
    # Server löschen
    try:
        import shutil
        shutil.rmtree(server_path)
        return response.json({"message": f"Server {server_name} deleted"})
    except Exception as e:
        return response.json({"error": f"Failed to delete server: {str(e)}"}, status=500)

@app.route("/api/system/stats", methods=["GET"])
@protected()
async def get_system_stats(request):
    # CPU-Auslastung
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # RAM-Auslastung
    memory = psutil.virtual_memory()
    
    # Festplattennutzung
    disk = psutil.disk_usage("/")
    
    # Netzwerkstatistiken
    net_io = psutil.net_io_counters()
    
    return response.json({
        "cpu": {
            "percent": cpu_percent,
            "cores": psutil.cpu_count()
        },
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        },
        "network": {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv
        },
        "timestamp": datetime.now().isoformat()
    })

# Statische Dateien für das Frontend bereitstellen
app.static("/", "./frontend/dist/index.html")
app.static("/static", "./frontend/dist/static")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

## 2. Frontend (HTML, CSS, JavaScript)

```html
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CraftForge - Minecraft Server Hosting Panel</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        :root {
            --primary-color: #e63946;
            --primary-dark: #c1121f;
            --primary-light: #ff6b6b;
            --dark-bg: #1c1c1c;
            --dark-panel: #2a2a2a;
            --light-gray: #f1faee;
            --medium-gray: #a8dadc;
            --text-color: #f1faee;
            --accent-blue: #457b9d;
            --accent-dark-blue: #1d3557;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: var(--dark-bg);
            color: var(--text-color);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* Header */
        .header {
            background-color: var(--dark-panel);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid var(--primary-color);
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .logo h1 {
            font-weight: 700;
            color: var(--primary-color);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .logo i {
            font-size: 2rem;
            color: var(--primary-color);
        }

        .user-menu {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .user-menu button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .user-menu button:hover {
            background-color: var(--primary-dark);
        }

        /* Main container */
        .container {
            display: flex;
            flex: 1;
        }

        /* Sidebar */
        .sidebar {
            width: 250px;
            background-color: var(--dark-panel);
            padding: 1.5rem 0;
            border-right: 1px solid #333;
        }

        .sidebar-menu {
            list-style: none;
        }

        .sidebar-menu li {
            margin-bottom: 0.5rem;
        }

        .sidebar-menu a {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem 1.5rem;
            text-decoration: none;
            color: var(--text-color);
            font-weight: 500;
            transition: all 0.3s;
            border-left: 3px solid transparent;
        }

        .sidebar-menu a:hover,
        .sidebar-menu a.active {
            background-color: rgba(230, 57, 70, 0.1);
            border-left-color: var(--primary-color);
            color: var(--primary-light);
        }

        .sidebar-menu i {
            width: 20px;
            text-align: center;
        }

        /* Main content */
        .content {
            flex: 1;
            padding: 2rem;
        }

        .page-title {
            margin-bottom: 2rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--primary-color);
            color: var(--text-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* Server cards */
        .servers-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
        }

        .server-card {
            background-color: var(--dark-panel);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            position: relative;
        }

        .server-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.2);
        }

        .server-status {
            position: absolute;
            top: 1rem;
            right: 1rem;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #888;
        }

        .server-status.online {
            background-color: #4caf50;
            box-shadow: 0 0 8px #4caf50;
        }

        .server-status.offline {
            background-color: #f44336;
            box-shadow: 0 0 8px #f44336;
        }

        .server-header {
            background-color: rgba(230, 57, 70, 0.9);
            padding: 1.5rem;
            position: relative;
        }

        .server-name {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .server-version {
            font-size: 0.9rem;
            opacity: 0.8;
        }

        .server-body {
            padding: 1.5rem;
        }

        .server-stat {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.75rem;
        }

        .server-stat-label {
            opacity: 0.7;
        }

        .server-actions {
            display: flex;
            justify-content: space-between;
            margin-top: 1.5rem;
            gap: 0.5rem;
        }

        .btn {
            background-color: var(--dark-bg);
            color: var(--text-color);
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            flex: 1;
        }

        .btn-primary {
            background-color: var(--primary-color);
        }

        .btn-primary:hover {
            background-color: var(--primary-dark);
        }

        .btn-secondary {
            background-color: var(--accent-blue);
        }

        .btn-secondary:hover {
            background-color: var(--accent-dark-blue);
        }

        /* Form styles */
        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }

        .form-control {
            width: 100%;
            padding: 0.75rem;
            border-radius: 4px;
            border: 1px solid #444;
            background-color: var(--dark-bg);
            color: var(--text-color);
            font-size: 1rem;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(230, 57, 70, 0.2);
        }

        /* Modal */
        .modal-backdrop {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .modal {
            background-color: var(--dark-panel);
            border-radius: 10px;
            width: 90%;
            max-width: 600px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }

        .modal-header {
            padding: 1.5rem;
            border-bottom: 1px solid #444;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .modal-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--primary-color);
        }

        .modal-close {
            background: none;
            border: none;
            color: var(--text-color);
            font-size: 1.5rem;
            cursor: pointer;
        }

        .modal-body {
            padding: 1.5rem;
        }

        .modal-footer {
            padding: 1.5rem;
            border-top: 1px solid #444;
            display: flex;
            justify-content: flex-end;
            gap: 1rem;
        }

        /* Terminal */
        .terminal {
            background-color: #1a1a1a;
            color: #f0f0f0;
            font-family: monospace;
            padding: 1rem;
            border-radius: 4px;
            margin-top: 1rem;
            height: 300px;
            overflow-y: auto;
        }

        .terminal-line {
            margin-bottom: 0.25rem;
            line-height: 1.5;
        }

        .terminal-input {
            display: flex;
            margin-top: 1rem;
        }

        .terminal-input input {
            flex: 1;
            background-color: #1a1a1a;
            color: #f0f0f0;
            border: 1px solid #444;
            padding: 0.5rem;
            font-family: monospace;
        }

        .terminal-input button {
            padding: 0.5rem 1rem;
            background-color: var(--primary-color);
            color: white;
            border: none;
            cursor: pointer;
        }

        /* System stats */
        .stats-cards {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background-color: var(--dark-panel);
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .stat-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
            font-weight: 500;
            color: var(--primary-light);
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .stat-subtitle {
            font-size: 0.9rem;
            opacity: 0.7;
        }

        .progress-bar {
            height: 8px;
            background-color: #444;
            border-radius: 4px;
            margin-top: 1rem;
            overflow: hidden;
        }

        .progress-value {
            height: 100%;
            background-color: var(--primary-color);
            border-radius: 4px;
            transition: width 0.3s ease;
        }

        /* Login page */
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: var(--dark-bg);
        }

        .login-card {
            background-color: var(--dark-panel);
            border-radius: 10px;
            padding: 2rem;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }

        .login-title {
            text-align: center;
            margin-bottom: 2rem;
            color: var(--primary-color);
            font-size: 2rem;
            font-weight: 700;
        }

        .login-form {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .login-btn {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 0.75rem;
            border-radius: 4px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.3s;
        }

        .login-btn:hover {
            background-color: var(--primary-dark);
        }
    </style>
</head>
<body>
    <div id="app">
        <!-- Login View (shown if not authenticated) -->
        <div v-if="!isAuthenticated" class="login-container">
            <div class="login-card">
                <h1 class="login-title">CraftForge</h1>
                <form class="login-form" @submit.prevent="login">
                    <div class="form-group">
                        <label class="form-label" for="username">Benutzername</label>
                        <input 
                            type="text" 
                            id="username" 
                            class="form-control" 
                            v-model="loginForm.username" 
                            required
                        >
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="password">Passwort</label>
                        <input 
                            type="password" 
                            id="password" 
                            class="form-control" 
                            v-model="loginForm.password" 
                            required
                        >
                    </div>
                    <button type="submit" class="login-btn">Anmelden</button>
                </form>
            </div>
        </div>

        <!-- Main Application (shown if authenticated) -->
        <div v-else>
            <!-- Header -->
            <header class="header">
                <div class="logo">
                    <i class="fas fa-cube"></i>
                    <h1>CraftForge</h1>
                </div>
                <div class="user-menu">
                    <button @click="logout">
                        <i class="fas fa-sign-out-alt"></i>
                        Abmelden
                    </button>
                </div>
            </header>

            <!-- Main Container -->
            <div class="container">
                <!-- Sidebar -->
                <aside class="sidebar">
                    <ul class="sidebar-menu">
                        <li>
                            <a href="#" @click.prevent="setActivePage('dashboard')" :class="{ active: activePage === 'dashboard' }">
                                <i class="fas fa-tachometer-alt"></i>
                                Dashboard
                            </a>
                        </li>
                        <li>
                            <a href="#" @click.prevent="setActivePage('servers')" :class="{ active: activePage === 'servers' }">
                                <i class="fas fa-server"></i>
                                Server
                            </a>
                        </li>
                        <li>
                            <a href="#" @click.prevent="setActivePage('system')" :class="{ active: activePage === 'system' }">
                                <i class="fas fa-microchip"></i>
                                System
                            </a>
                        </li>
                        <li>
                            <a href="#" @click.prevent="setActivePage('settings')" :class="{ active: activePage === 'settings' }">
                                <i class="fas fa-cog"></i>
                                Einstellungen
                            </a>
                        </li>
                    </ul>
                </aside>

                <!-- Main Content -->
                <main class="content">
                    <!-- Dashboard Page -->
                    <div v-if="activePage === 'dashboard'">
                        <div class="page-title">
                            <h2>Dashboard</h2>
                        </div>
                        
                        <!-- System Stats Overview -->
                        <div class="stats-cards">
                            <div class="stat-card">
                                <div class="stat-title">
                                    <i class="fas fa-microchip"></i>
                                    CPU-Auslastung
                                </div>
                                <div class="stat-value">{{ systemStats.cpu.percent }}%</div>
                                <div class="progress-bar">
                                    <div class="progress-value" :style="{ width: systemStats.cpu.percent + '%' }"></div>
                                </div>
                            </div>
                            
                            <div class="stat-card">
                                <div class="stat-title">
                                    <i class="fas fa-memory"></i>
                                    RAM-Auslastung
                                </div>
                                <div class="stat-value">{{ systemStats.memory.percent }}%</div>
                                <div class="stat-subtitle">{{ formatBytes(systemStats.memory.used) }} / {{ formatBytes(systemStats.memory.total) }}</div>
                                <div class="progress-bar">
                                    <div class="progress-value" :style="{ width: systemStats.memory.percent + '%' }"></div>
                                </div>
                            </div>
                            
                            <div class="stat-card">
                                <div class="stat-title">
                                    <i class="fas fa-hdd"></i>
                                    Speicherplatz
                                </div>
                                <div class="stat-value">{{ systemStats.disk.percent }}%</div>
                                <div class="stat-subtitle">{{ formatBytes(systemStats.disk.used) }} / {{ formatBytes(systemStats.disk.total) }}</div>
                                <div class="progress-bar">
                                    <div class="progress-value" :style="{ width: systemStats.disk.percent + '%' }"></div>
                                </div>
                            </div>
                            
                            <div class="stat-card">
                                <div class="stat-title">
                                    <i class="fas fa-server"></i>
                                    Online Server
                                </div>
                                <div class="stat-value">{{ getOnlineServersCount() }} / {{ servers.length }}</div>
                            </div>
                        </div>
                        
                        <!-- Recent Servers -->
                        <div class="page-title">
                            <h3>Aktive Server</h3>
                        </div>
                        
                        <div class="servers-grid">
                            <div class="server-card" v-for="server in getRunningServers()" :key="server.name">
                                <div class="server-status online"></div>
                                <div class="server-header">
                                    <div class="server-name">{{ server.name }}</div>
                                    <div class="server-version">Version: {{ server.version || 'Unbekannt' }}</div>
                                </div>
                                <div class="server-body">
                                    <div class="server-stat">
                                        <span class="server-stat-label">Port:</span>
                                        <span>{{ server.port }}</span>
                                    </div>
                                    <div class="server-actions">
                                        <button class="btn btn-primary" @click="openServerConsole(server)">
                                            <i class="fas fa-terminal"></i>
                                            Konsole
                                        </button>
                                        <button class="btn btn-secondary" @click="stopServer(server)">
                                            <i class="fas fa-stop"></i>
                                            Stoppen
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Servers Page -->
                    <div v-if="activePage === 'servers'">
                        <div class="page-title">
                            <h2>Minecraft Server</h2>
                            <button class="btn btn-primary" @click="showNewServerModal = true">
                                <i class="fas fa-plus"></i>
                                Neuer Server
                            </button>
                        </div>
                        
                        <div class="servers-grid">
                            <div class="server-card" v-for="server in servers" :key="server.name">
                                <div class="server-status" :class="server.running ? 'online' : 'offline'"></div>
                                <div class="server-header">
                                    <div class="server-name">{{ server.name }}</div>
                                    <div class="server-version">Version: {{ server.version || 'Unbekannt' }}</div>
                                </div>
                                <div class="server-body">
                                    <div class="server-stat">
                                        <span class="server-stat-label">Status:</span>
                                        <span>{{ server.running ? 'Online' : 'Offline' }}</span>
                                    </div>
                                    <div class="server-stat">
                                        <span class="server-stat-label">Port:</span>
                                        <span>{{ server.port }}</span>
                                    </div>
                                    <div class="server-actions">
                                        <button 
                                            class="btn" 
                                            :class="server.running ? 'btn-secondary' : 'btn-primary'"
                                            @click="server.running ? stopServer(server) : startServer(server)"
                                        >
                                            <i class="fas" :class="server.running ? 'fa-stop' : 'fa-play'"></i>
                                            {{ server.running ? 'Stoppen' : 'Starten' }}
                                        </button>
                                        <button class="btn btn-secondary" @click="openServerConsole(server)">
                                            <i class="fas fa-terminal"></i>
                                        </button>
                                    </div>
                                    <div class="server-actions" style="margin-top: 0.5rem;">
                                        <button class="btn" @click="openServerSettings(server)">
                                            <i class="fas fa-cog"></i>
                                            Einstellungen
                                        </button>
                                        <button class="btn" @click="confirmDeleteServer(server)" style="color: var(--primary-light);">
                                            <i class="fas fa-trash"></i>
                                            Löschen
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- System Page -->
                    <div v-if="activePage === 'system'">
                        <div class="page-title">
                            <h2>Systemüberwachung</h2>
                        </div>
                        
                        <!-- Detailed System Stats -->
                        <div class="stats-cards">
                            <div class="stat-card">
                                <div class="stat-title">
                                    <i class="fas fa-microchip"></i>
                                    CPU-Auslastung
                                </div>
                                <div class="stat-value">{{ systemStats.cpu.percent }}%</div>
                                <div class="stat-subtitle">{{ systemStats.cpu.cores }} Kerne</div>
                                <div class="progress-bar">
                                    <div class="progress-value" :style="{ width: systemStats.cpu.percent + '%' }"></div>
                                </div>
                            </div>
                            
                            <div class="stat-card">
                                <div class="stat-title">
                                    <i class="fas fa-memory"></i>
                                    RAM-Auslastung
                                </div>
                                <div class="stat-value">{{ systemStats.memory.percent }}%</div>
                                <div class="stat-subtitle">{{ formatBytes(systemStats.memory.used) }} / {{ formatBytes(systemStats.memory.total) }}</div>
                                <div class="progress-bar">
                                    <div class="progress-value" :style="{ width: systemStats.memory.percent + '%' }"></div>
                                </div>
                            </div>
                            
                            <div class="stat-card">
                                <div class="stat-title">
                                    <i class="fas fa-hdd"></i>
                                    Speicherplatz
                                </div>
                                <div class="stat-value">{{ systemStats.disk.percent }}%</div>
                                <div class="stat-subtitle">{{ formatBytes(systemStats.disk.used) }} / {{ formatBytes(systemStats.disk.total) }}</div>
                                <div class="progress-bar">
                                    <div class="progress-value" :style="{ width: systemStats.disk.percent + '%' }"></div>
                                </div>
                            </div>
                            
                            <div class="stat-card">
                                <div class="stat-title">
                                    <i class="fas fa-network-wired"></i>
                                    Netzwerk
                                </div>
                                <div class="stat-subtitle">Gesendet: {{ formatBytes(systemStats.network.bytes_sent) }}</div>
                                <div class="stat-subtitle">Empfangen: {{ formatBytes(systemStats.network.bytes_recv) }}</div>
                            </div>
                        </div>
                    </div>

                    <!-- Settings Page -->
                    <div v-if="activePage === 'settings'">
                        <div class="page-title">
                            <h2>Einstellungen</h2>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Default-Speicherort für Server</label>
                            <input type="text" class="form-control" v-model="settings.serverDir" readonly>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Standard RAM pro Server (MB)</label>
                            <input type="number" class="form-control" v-model="settings.defaultRam">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Automatisches Backup</label>
                            <select class="form-control" v-model="settings.backupInterval">
                                <option value="none">Deaktiviert</option>
                                <option value="daily">Täglich</option>
                                <option value="weekly">Wöchentlich</option>
                                <option value="monthly">Monatlich</option>
                            </select>
                        </div>
                        
                        <button class="btn btn-primary" @click="saveSettings">
                            <i class="fas fa-save"></i>
                            Einstellungen speichern
                        </button>
                    </div>
                </main>
            </div>

            <!-- New Server Modal -->
            <div class="modal-backdrop" v-if="showNewServerModal">
                <div class="modal">
                    <div class="modal-header">
                        <h3 class="modal-title">Neuen Minecraft-Server erstellen</h3>
                        <button class="modal-close" @click="showNewServerModal = false">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="form-group">
                            <label class="form-label" for="serverName">Servername</label>
                            <input type="text" id="serverName" class="form-control" v-model="newServer.name" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="serverVersion">Minecraft Version</label>
                            <select id="serverVersion" class="form-control" v-model="newServer.version">
                                <option value="1.20.1">1.20.1</option>
                                <option value="1.19.4">1.19.4</option>
                                <option value="1.18.2">1.18.2</option>
                                <option value="1.17.1">1.17.1</option>
                                <option value="1.16.5">1.16.5</option>
                                <option value="1.12.2">1.12.2</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="serverPort">Port</label>
                            <input type="number" id="serverPort" class="form-control" v-model="newServer.port" min="1024" max="65535">
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="serverRam">RAM (MB)</label>
                            <input type="number" id="serverRam" class="form-control" v-model="newServer.ram" min="512">
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn" @click="showNewServerModal = false">Abbrechen</button>
                        <button class="btn btn-primary" @click="createServer">Erstellen</button>
                    </div>
                </div>
            </div>

            <!-- Server Console Modal -->
            <div class="modal-backdrop" v-if="showConsoleModal">
                <div class="modal">
                    <div class="modal-header">
                        <h3 class="modal-title">Konsole: {{ selectedServer ? selectedServer.name : '' }}</h3>
                        <button class="modal-close" @click="showConsoleModal = false">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="terminal">
                            <div class="terminal-line" v-for="(line, index) in serverLogs" :key="index">{{ line }}</div>
                        </div>
                        <div class="terminal-input">
                            <input 
                                type="text" 
                                v-model="consoleCommand" 
                                @keyup.enter="sendCommand"
                                placeholder="Befehl eingeben..."
                            >
                            <button @click="sendCommand">Senden</button>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn" @click="refreshLogs">
                            <i class="fas fa-sync"></i>
                            Aktualisieren
                        </button>
                        <button class="btn btn-primary" @click="showConsoleModal = false">Schließen</button>
                    </div>
                </div>
            </div>

            <!-- Server Settings Modal -->
            <div class="modal-backdrop" v-if="showServerSettingsModal">
                <div class="modal">
                    <div class="modal-header">
                        <h3 class="modal-title">Einstellungen: {{ selectedServer ? selectedServer.name : '' }}</h3>
                        <button class="modal-close" @click="showServerSettingsModal = false">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="form-group" v-for="(value, key) in serverProperties" :key="key">
                            <label class="form-label">{{ key }}</label>
                            <input type="text" class="form-control" v-model="serverProperties[key]">
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn" @click="showServerSettingsModal = false">Abbrechen</button>
                        <button class="btn btn-primary" @click="saveServerSettings">Speichern</button>
                    </div>
                </div>
            </div>

            <!-- Delete Confirmation Modal -->
            <div class="modal-backdrop" v-if="showDeleteConfirmModal">
                <div class="modal">
                    <div class="modal-header">
                        <h3 class="modal-title">Server löschen</h3>
                        <button class="modal-close" @click="showDeleteConfirmModal = false">&times;</button>
                    </div>
                    <div class="modal-body">
                        <p>Bist du sicher, dass du den Server "{{ selectedServer ? selectedServer.name : '' }}" löschen möchtest?</p>
                        <p style="color: var(--primary-light);">Diese Aktion kann nicht rückgängig gemacht werden!</p>
                    </div>
                    <div class="modal-footer">
                        <button class="btn" @click="showDeleteConfirmModal = false">Abbrechen</button>
                        <button class="btn btn-primary" style="background-color: var(--primary-dark);" @click="deleteServer">Löschen</button>
                    </div>
                </div>
            </div>
        </div>
            