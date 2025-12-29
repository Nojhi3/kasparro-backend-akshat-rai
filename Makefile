# Run the system
up:
	docker compose up --build -d

# Stop the system
down:
	docker compose down

# Run tests (We will implement the test container later)
test:
	docker compose exec app pytest

# Helper: Clean up pycache
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
