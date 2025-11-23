.PHONY: help setup dev build test clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make setup    - Configura o ambiente de desenvolvimento"
	@echo "  make dev      - Inicia o ambiente de desenvolvimento"
	@echo "  make build    - Build das imagens Docker"
	@echo "  make test     - Roda os testes"
	@echo "  make clean    - Limpa containers e volumes"

setup:
	@echo "Configurando ambiente..."
	cd backend && python -m venv venv
	cd backend && source venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install
	@echo "Ambiente configurado!"

dev:
	docker-compose up -d

build:
	docker-compose build

test:
	cd backend && pytest
	cd frontend && npm test

clean:
	docker-compose down -v
	docker system prune -f




