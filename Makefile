PYTHON = python3
PIP = pip3

.PHONY: all
all: install run

# Install requirements
.PHONY: install
install:
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed successfully."

# Run the Streamlit application
.PHONY: run
run:
	@echo "Launching Work Analytics Dashboard..."
	streamlit run main.py

# Clean up virtual environment and cached files
.PHONY: clean
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	@echo "Cleanup complete."

# Create requirements.txt
.PHONY: freeze
freeze:
	@echo "Generating requirements.txt..."
	$(PIP) freeze > requirements.txt
	@echo "requirements.txt updated."

# Help target
.PHONY: help
help:
	@echo "Work Analytics Dashboard Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  all      - Install dependencies, and run app (default)"
	@echo "  install  - Install project dependencies"
	@echo "  run      - Launch Streamlit application"
	@echo "  clean    - Remove virtual environment and cached files"
	@echo "  freeze   - Generate requirements.txt from current environment"
	@echo "  help     - Show this help message"