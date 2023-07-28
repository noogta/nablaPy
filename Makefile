# Makefile to install required Python libraries and external modules

# Define the Python interpreter to use
PYTHON := /bin/python3

# Define the required libraries
LIBRARIES := numpy scipy

# Define the external modules
EXTERNAL_MODULES := readgssi matplotlib PyQt6

# Targets
all: install_external install_libraries

install_external:
	@echo "Installing external Python modules..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install $(EXTERNAL_MODULES)
	@echo "External modules installation completed."

install_libraries:
	@echo "Installing required Python libraries..."
	$(PYTHON) -m pip install $(LIBRARIES)
	@echo "Libraries installation completed."

.PHONY: install_external install_libraries

