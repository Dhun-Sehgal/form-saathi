"""Background worker: `python -m app.worker`.

Runs the notification + expiry jobs every 30 minutes. On hosts without a worker process,
`flask run-jobs` can be called from any cron service instead; the dashboard also generates
a user's notifications on load, so nothing depends on the worker being present.
"""
import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from . import create_app
from .services.notify import run_all

log = logging.getLogger("formsaathi.worker")


def main() -> None:
    app = create_app()

    def job():
        with app.app_context():
            log.info("Jobs finished: %s", run_all())

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(job, "interval", minutes=30, id="notifications", next_run_time=None)
    job()
    log.info("Worker started; running jobs every 30 minutes.")
    scheduler.start()


if __name__ == "__main__":
    main()
