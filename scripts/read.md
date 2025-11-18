# 1 without A2A
streamlit run ui/app.py --server.port 8501


# 2 with A2A if we use it
python scripts/start_agents.py & streamlit run ui/a2a_app.py --server.port 8502