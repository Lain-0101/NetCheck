import json
import subprocess
import socket
import sys
from datetime import datetime

def load_config(filename="config.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: O arquivo de configuração '{filename}' não foi encontrado.")
        sys.exit(1)

def ping_host(address):
    """Envia 1 pacote de ping para o endereço para checar se está respondendo."""
    try:
        # No Linux, o comando ping envia pacotes. -c 1 (1 pacote), -W 2 (timeout de 2 segundos)
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", address],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception:
        return False

def check_port(address, port):
    """Verifica se uma porta TCP específica está aberta no host."""
    try:
        with socket.create_connection((address, port), timeout=2):
            return True
    except (socket.timeout, socket.error):
        return False

def log_message(message):
    """Exibe no terminal e salva a mensagem no arquivo de log."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_line = f"{timestamp} {message}"
    print(log_line)
    with open("netcheck.log", "a") as log_file:
        log_file.write(log_line + "\n")

def main():
    config = load_config()
    log_message("=== Iniciando varredura NetCheck ===")
    
    for item in config.get("hosts", []):
        name = item.get("name")
        address = item.get("address")
        ports = item.get("ports", [])
        
        # Teste de Ping
        is_online = ping_host(address)
        status_ping = "ONLINE 🟢" if is_online else "OFFLINE 🔴"
        log_message(f"Host: {name} ({address}) -> Ping: {status_ping}")
        
        # Teste de Portas
        for port in ports:
            is_port_open = check_port(address, port)
            status_port = "ABERTA 🔓" if is_port_open else "FECHADA 🔒"
            log_message(f"   ↳ Porta {port}: {status_port}")

    log_message("=== Varredura finalizada ===\n")

if __name__ == "__main__":
    main()