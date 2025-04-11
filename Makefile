.PHONY: install uninstall run migrate seed-users test

VENV_DIR=venv/alma
VENV_BIN=$(VENV_DIR)/bin
DB_FILE=leads.db

install:
	python3 -m venv $(VENV_DIR)
	$(VENV_BIN)/pip install --upgrade pip
	$(VENV_BIN)/pip install -r requirements.txt
# 	$(MAKE) migrate
# 	$(MAKE) seed-users

uninstall:
	rm -rf $(VENV_DIR)
	rm -f $(DB_FILE)

run:
	$(VENV_BIN)/uvicorn app.main:app --reload


migrate:
	$(VENV_BIN)/alembic upgrade head

seed-users:
	$(VENV_BIN)/python scripts/seed_users.py

test:
	$(VENV_BIN)/pytest tests
