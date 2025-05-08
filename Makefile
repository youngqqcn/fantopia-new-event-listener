stop:
	ps aux | grep 'python get_fantopia_events_task.py' | grep -v grep | awk '{print $$2}' | xargs kill
start:
	nohup .venv/bin/python get_fantopia_events_task.py > task.log 2>&1 &