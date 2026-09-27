import click
from flask.cli import with_appcontext

from app.services.auth_service import AuthService


@click.command("create-admin")
@click.option(
    "--first-name",
    prompt="Nombre",
)
@click.option(
    "--last-name",
    prompt="Apellido",
)
@click.option(
    "--email",
    prompt="Email",
)
@click.option(
    "--password",
    prompt="Contraseña",
    hide_input=True,
    confirmation_prompt=True,
)
@with_appcontext
def create_admin_command(
    first_name,
    last_name,
    email,
    password,
):
    try:
        user = AuthService.create_admin(
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": password,
            }
        )
    except (
        ValueError,
        FileExistsError,
        RuntimeError,
    ) as error:
        raise click.ClickException(
            str(error)
        ) from error

    click.echo(
        f"Administrador creado correctamente: {user.email}"
    )