.PHONY: api streamlit dev

api:
	python3 -m uvicorn app.main:app --reload --host localhost --port 8000

streamlit:
	streamlit run streamlit_app.py

dev:
	@echo "Starting API and Streamlit client..."
	@sh run_dev.sh
