#!/bin/bash
# Script para criar ícones PWA (placeholder)
# Em produção, substitua por ícones reais

# Criar ícone 192x192 (placeholder SVG convertido)
convert -size 192x192 xc:#2563eb -pointsize 72 -fill white -gravity center -annotate +0+0 "VC" icon-192x192.png 2>/dev/null || echo "ImageMagick não instalado - use ícones reais"

# Criar ícone 512x512 (placeholder SVG convertido)
convert -size 512x512 xc:#2563eb -pointsize 200 -fill white -gravity center -annotate +0+0 "VC" icon-512x512.png 2>/dev/null || echo "ImageMagick não instalado - use ícones reais"

echo "Ícones criados (ou use ícones reais)"
