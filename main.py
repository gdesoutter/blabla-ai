import pyfiglet
import ollama
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.markdown import Markdown
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import ANSI

historique = []
ai_model = "qwen3:8b"
username = "Guillaume"


banner = pyfiglet.figlet_format("BLABLA AI", font="slant")
banner_centered = Align.center(f"[bold green]{banner}[/]")
console = Console()
console.print(banner_centered)
console.print("(Tape 'exit' pour quitter)")
while True:
    prompt_style = ANSI(f"\x1b[1;32m{username} > \x1b[0m")
    user_input = prompt(prompt_style)
    #user_input = console.input(f"[bold green]{username} > [/]")
    if user_input.lower() in ['exit', 'quit']:
        break
    historique.append({'role':'user', 'content': user_input})
    with console.status("[bold green] Thinking...", spinner="earth"):
        client = ollama.Client(host='http://macmini:11434')
        response = client.chat(model=ai_model, messages=historique)
        response_text = response['message']['content']
    historique.append({'role':'assistant', 'content': response_text})
    response_formatted = Markdown(response_text)
    console.print(Panel(response_formatted, title=ai_model, border_style="magenta"))