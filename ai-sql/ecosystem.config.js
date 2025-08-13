module.exports = {
	apps : [{
		name: 'ai-sql-backend-fastapi',
		script: 'uvicorn',
		args: 'app:app --host 0.0.0.0 --port 8080',
		interpreter: 'python3',
		cwd: '/home/yash/ai-with-sql/ai-sql',
	},{
		name: 'ai-sql-frontend-streamlit',
		script: 'streamlit',
		args: 'run ui.py --server.port 8501',
		interpreter: 'python3',
		cwd: '/home/yash/ai-with-sql/ai-sql',
	}]
};
