import sys
sys.path.append('.')
from src.tasks import process_n8n_webhook_task

print(type(process_n8n_webhook_task))
task = process_n8n_webhook_task.delay({"event_type": "SOCIAL_COMMENT"})
print(type(task))
print(task.id)
