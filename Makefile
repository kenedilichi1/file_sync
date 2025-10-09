.PHONY: install run test clean build dist install-dev setup-scripts

# Platform detection
UNAME_S := $(shell uname -s)

# Colors for output
ifneq (,$(findstring Darwin,$(UNAME_S)))
    # macOS
    BLUE := \033[34m
    GREEN := \033[32m
    RED := \033[31m
    RESET := \033[0m
else
    # Linux and others
    BLUE := \033[34m
    GREEN := \033[32m
    RED := \033[31m
    RESET := \033[0m
endif

setup-scripts:
	@echo "$(BLUE)🔧 Setting up script permissions...$(RESET)"
	@if [ "$(UNAME_S)" = "Darwin" ] || [ "$(UNAME_S)" = "Linux" ]; then \
		chmod +x scripts/*.sh; \
		echo "$(GREEN)✅ Script permissions set$(RESET)"; \
	fi

install: setup-scripts
	@echo "$(BLUE)🚀 Installing FileSync...$(RESET)"
	@if [ "$(UNAME_S)" = "Darwin" ] || [ "$(UNAME_S)" = "Linux" ]; then \
		./scripts/install.sh; \
	elif [ "$(UNAME_S)" = "Windows" ] || [ "$(UNAME_S)" = "MINGW" ] || [ "$(UNAME_S)" = "CYGWIN" ]; then \
		./scripts/install.bat; \
	else \
		echo "$(RED)❌ Unsupported platform: $(UNAME_S)$(RESET)"; \
		exit 1; \
	fi

run: setup-scripts
	@echo "$(BLUE)🚀 Starting FileSync...$(RESET)"
	@if [ "$(UNAME_S)" = "Darwin" ] || [ "$(UNAME_S)" = "Linux" ]; then \
		./scripts/run.sh; \
	elif [ "$(UNAME_S)" = "Windows" ] || [ "$(UNAME_S)" = "MINGW" ] || [ "$(UNAME_S)" = "CYGWIN" ]; then \
		./scripts/run.bat; \
	else \
		echo "$(RED)❌ Unsupported platform: $(UNAME_S)$(RESET)"; \
		exit 1; \
	fi

test:
	@echo "$(BLUE)🧪 Running tests...$(RESET)"
	python -m pytest tests/ -v

clean:
	@echo "$(BLUE)🧹 Cleaning up...$(RESET)"
	rm -rf build/ dist/ *.egg-info filesync_env/ __pycache__/ .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

build:
	@echo "$(BLUE)📦 Building package...$(RESET)"
	python -m build

install-dev: install
	@echo "$(BLUE)📚 Installing development dependencies...$(RESET)"
	pip install -e ".[dev]"

help:
	@echo "$(GREEN)FileSync Build Commands:$(RESET)"
	@echo "  $(BLUE)setup-scripts$(RESET) - Make scripts executable"
	@echo "  $(BLUE)install$(RESET)      - Install FileSync in virtual environment"
	@echo "  $(BLUE)run$(RESET)         - Run FileSync"
	@echo "  $(BLUE)test$(RESET)        - Run tests"
	@echo "  $(BLUE)clean$(RESET)       - Clean build artifacts"
	@echo "  $(BLUE)build$(RESET)       - Build distribution packages"
	@echo "  $(BLUE)install-dev$(RESET)  - Install with development dependencies"