import sys
import traceback

class DummyMod: pass
sys.modules['celery'] = DummyMod()
sys.modules['celery.schedules'] = DummyMod()

try:
    import src.main
    print('SUCCESS')
except Exception as e:
    traceback.print_exc()

