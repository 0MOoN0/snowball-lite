import pytest




@pytest.mark.usefixtures('app', "client", "session")
class TestScheduler:

    def test_get_scheduler(self):
        """
        Test to get the scheduler
        """
        from web.scheduler import scheduler
        scheduler_scheduler = scheduler.scheduler
        pass
