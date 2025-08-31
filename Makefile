# =========================
# Oleve Project Makefile (final, English)
# =========================
#✅ How to use

#Install everything: --------------

#make install


#Run backend:-------------

#make run-backend


#Run frontend:----------------

#make run-frontend


#Run both backend + frontend: ------------

#make run-all


#Run Python tests: ----------------

#make test


#Open shell with virtual environment activated:------------

#make shell


#Reinstall everything from scratch: -------------

#make reinstall


#Clean virtual environment:--------------------

#make clean



VENV = .venv

# Detect OS
ifeq ($(OS),Windows_NT)
    PYTHON = $(VENV)\Scripts\python.exe
    PIP = $(VENV)\Scripts\pip.exe
else
    PYTHON = $(VENV)/bin/python
    PIP = $(VENV)/bin/pip
endif

# -------------------------
# 1) Install dependencies and setup environment
# -------------------------
install:
	@echo "Creating virtual environment and installing dependencies..."
	python -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PYTHON) -m playwright install --with-deps chromium
	cd frontend && npm install

# -------------------------
# 2) Run backend (FastAPI)
# -------------------------
run-backend:
	@echo "Running backend (FastAPI) on port 8080..."
	uvicorn app.main:app --reload --host 127.0.0.1 --port 8080

# -------------------------
# 3) Run frontend (React)
# -------------------------
run-frontend:
ifeq ($(OS),Windows_NT)
	start cmd /k "cd frontend && npm start"
else
	cd frontend && npm start
endif

# -------------------------
# 4) Run both backend + frontend (development)
# -------------------------
run-all:
	@echo "Running backend + frontend..."
	@$(MAKE) run-backend &
	@$(MAKE) run-frontend &

# -------------------------
# 5) Run Python tests
# -------------------------
test:
	$(PYTHON) -m pytest backend/tests -v --maxfail=1 --disable-warnings

# -------------------------
# 6) Open shell with virtual environment activated
# -------------------------
shell:
ifeq ($(OS),Windows_NT)
	@echo "Launching shell with virtualenv activated..."
	@cmd /k "$(VENV)\Scripts\activate.bat"
else
	@echo "Launching shell with virtualenv activated..."
	@bash -c "source $(VENV)/bin/activate && exec bash"
endif

# -------------------------
# 7) Reinstall everything from scratch
# -------------------------
reinstall: clean install

# -------------------------
# 8) Clean virtual environment
# -------------------------
clean:
ifeq ($(OS),Windows_NT)
	rmdir /s /q $(VENV)
else
	rm -rf $(VENV)
endif
