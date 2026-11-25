import os

import click
import sqlalchemy as sa
from flask import Flask


def register_cli(app: Flask) -> None:
    @app.cli.command("seed-reference")
    def seed_reference_cmd():
        """Load states, categories and document types (safe to re-run)."""
        from .reference import seed_reference

        click.echo(f"Reference data ready. Newly created: {seed_reference()}")

    @app.cli.command("seed-opportunities")
    @click.option("--update", is_flag=True, help="Overwrite existing records with the data in shared/opportunities.json.")
    def seed_opportunities_cmd(update):
        """Load the real, source-checked opportunities from shared/opportunities.json (safe to re-run)."""
        from .official import seed_opportunities

        click.echo(f"Official opportunities: {seed_opportunities(update)}")

    @app.cli.command("purge-demo")
    def purge_demo_cmd():
        """Remove every demo opportunity (older installs loaded sample data)."""
        from .demo import purge_demo

        click.echo(f"Demo opportunities removed: {purge_demo()}")

    @app.cli.command("create-admin")
    @click.option("--email", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin_cmd(email, password):
        """Create (or promote) an admin account."""
        click.echo(ensure_admin(email, password))

    @app.cli.command("ensure-admin")
    def ensure_admin_cmd():
        """Create the admin from ADMIN_EMAIL / ADMIN_PASSWORD env vars if both are set (used on deploy)."""
        email, password = os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASSWORD")
        if not (email and password):
            click.echo("ADMIN_EMAIL / ADMIN_PASSWORD not set; skipping.")
            return
        click.echo(ensure_admin(email, password, reset_password=False))

    @app.cli.command("run-jobs")
    def run_jobs_cmd():
        """Expire past-deadline opportunities and generate notifications for everyone."""
        from ..services.notify import run_all

        click.echo(f"Jobs finished: {run_all()}")


def ensure_admin(email: str, password: str, reset_password: bool = True) -> str:
    from ..extensions import db
    from ..models import NotificationPreference, User, UserProfile
    from ..utils.auth import hash_password

    email = email.strip().lower()
    user = db.session.scalar(sa.select(User).where(User.email == email))
    if user is None:
        user = User(email=email, password_hash=hash_password(password), role="admin")
        user.profile = UserProfile(full_name="Admin")
        db.session.add(user)
        db.session.flush()
        db.session.add(NotificationPreference(user_id=user.id))
        msg = "Admin account created."
    else:
        user.role = "admin"
        if reset_password:
            user.password_hash = hash_password(password)
        msg = "Existing account is now an admin."
    db.session.commit()
    return msg
