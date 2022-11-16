import typer

from trainer import train


trainer = typer.Typer()
trainer.command()(train)

if __name__ == "__main__":
    trainer()
