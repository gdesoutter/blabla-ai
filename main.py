import pyfiglet
import ollama
import sys
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.markdown import Markdown
from rich.table import Table
from rich.syntax import Syntax # Import important pour le code !
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import ANSI

# --- CONFIGURATION ---
HOST = 'http://macmini:11434'
USERNAME = "Guillaume"
console = Console()

class BlablaAI:
    def __init__(self):
        self.client = ollama.Client(host=HOST)
        self.historique = []
        self.model = None
        self.session = None
        self.kb = KeyBindings()
        self._setup_bindings()

    def _setup_bindings(self):
        @self.kb.add('enter')
        def _(event):
            event.current_buffer.validate_and_handle()

        @self.kb.add('escape', 'enter')
        def _(event):
            event.current_buffer.insert_text('\n')

        @self.kb.add('c-c')
        def _(event):
            event.app.exit()

    def initialisation(self):
        banner = pyfiglet.figlet_format("BLABLA AI", font="slant")
        console.print(Align.center(f"[bold green]{banner}[/]"))
        
        try:
            models_info = self.client.list()
            available_models = [m.get('model') or m.get('name') for m in models_info.get('models', [])]
            
            table = Table(title="Modèles disponibles", show_header=True, header_style="bold magenta")
            table.add_column("N°", style="cyan", justify="right")
            table.add_column("Modèle", style="white")

            for i, name in enumerate(available_models, 1):
                table.add_row(str(i), name)
            console.print(table)

            while True:
                choix = console.input(f"[bold yellow]Choisis ton modèle (1-{len(available_models)}) : [/]")
                if choix.isdigit() and 1 <= int(choix) <= len(available_models):
                    self.model = available_models[int(choix) - 1]
                    break
            
            self.session = PromptSession(key_bindings=self.kb, multiline=True)
            console.print(f"[bold green]✓ {self.model} prêt ![/]\n")

        except Exception as e:
            console.print(f"[bold red]Erreur :[/] {e}")
            sys.exit(1)

    def lancer(self):
        while True:
            try:
                prompt_label = ANSI(f"\x1b[1;32m{USERNAME} > \x1b[0m")
                user_input = self.session.prompt(prompt_label)

                if user_input is None:
                    break
                
                user_input = user_input.strip()
                if not user_input: continue
                if user_input.lower() in ['exit', 'quit', 'quitter']: 
                    break

                if "```" in user_input:
                    display_content = Markdown(user_input)
                elif any(kw in user_input for kw in ["def ", "import ", "class ", "print(", "    "]):
                    display_content = Syntax(user_input, "python", theme="monokai", line_numbers=True)
                else:
                    display_content = user_input

                console.print(Panel(
                    display_content, 
                    title=f"[bold green]{USERNAME}[/]", 
                    border_style="green",
                    padding=(1, 2)
                ))

                self.historique.append({'role': 'user', 'content': user_input})

                with console.status(f"[bold green] {self.model} réfléchit...", spinner="earth"):
                    response = self.client.chat(model=self.model, messages=self.historique)
                    response_text = response['message']['content']

                self.historique.append({'role': 'assistant', 'content': response_text})
                
                console.print(Panel(
                    Markdown(response_text), 
                    title=f"[bold magenta]{self.model}[/]", 
                    border_style="magenta",
                    padding=(1, 2)
                ))
                console.print("")

            except (EOFError, KeyboardInterrupt):
                break
            except Exception as e:
                console.print(f"[bold red]Erreur :[/] {e}")

if __name__ == "__main__":
    app = BlablaAI()
    app.initialisation()
    app.lancer()
    console.print("[bold yellow]\nSession terminée. À bientôt ![/]")