from print_api.app import celery


@celery.task(name="test_celery_task")
def test_celery_task():
    """
    Test Celery Task
    """
    print("Celery task has been executed")
    return True