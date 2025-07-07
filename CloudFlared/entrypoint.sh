#!/bin/sh
echo "🌍 Iniciando Cloudflare Tunnel al cliente..."

# Esperar que el cliente esté disponible
until curl -s http://cliente1:8501 > /dev/null; do
  echo "⏳ Esperando a que el cliente esté listo..."
  sleep 2
done

# Lanzar túnel
echo "✅ Cliente activo. Iniciando túnel..."
exec cloudflared tunnel --url http://cliente1:8501
