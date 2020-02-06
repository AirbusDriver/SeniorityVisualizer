"""Commands for the 'user' package"""
import typing as t

import click
from flask.cli import with_appcontext

from .models import User, Role


def validate_username(username: str) -> str:
    return username


@click.command("add_user")
@with_appcontext
def create_user():
    """Add a new user"""

    username = click.prompt(f"Enter new user name")

    password = click.prompt(
        f"Enter password for user -> {username}",
        confirmation_prompt=True,
        hide_input=True,
    )

    company_email = click.prompt("Provide company email")

    personal_email = click.prompt("Provide personal email")

    if User.query.filter(User.username.ilike(username)).first():
        raise click.ClickException(f"{username} already taken")

    new_user = User(
        username=username,
        company_email=company_email,
        personal_email=personal_email,
        password=password,
    )

    roles = {str(i): val for i, val in enumerate(Role.query.all(), 1)}

    role_inp_str = f"Select Role for {username}"

    for k, role in roles.items():
        role_inp_str += f"\n{k}: {role}"

    role_selection = click.prompt(text=role_inp_str, type=str, confirmation_prompt=True)

    try:
        new_user.role = roles.get(role_selection)
        new_user.save()
    except Exception:
        click.echo(f"ERROR OCCURRED, {username} not added to db")
        raise
    else:
        click.echo(f"{username} added!")
