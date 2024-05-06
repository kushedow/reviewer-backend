from main import gc
from src import config
from src.classes.stats_manager import StatsManager

def test_return_data_by_id():
    stats_manager = StatsManager(gc, config.SHEET_IDS)
    stats = stats_manager.get_student_skills("22699947")
    print(stats)
    assert 1
