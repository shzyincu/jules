from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

class PromptManager:
    def __init__(self, template_dir: str = "src/agent/templates"):
        self.template_dir = template_dir
        # Ensure template dir exists
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)

        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml', 'jinja'])
        )

    def render_prompt(self, template_name: str, **kwargs) -> str:
        """Renders a prompt template."""
        # For simplicity, if template name doesn't end with .jinja, add it
        if not template_name.endswith(".jinja"):
             # We might have prompt templates and code templates.
             # Let's assume prompts are just text files or jinja files.
             # If file doesn't exist, maybe fallback to a default string or error.
             # For this skeleton, we'll try to load it.
             template_name += ".jinja"

        try:
            template = self.env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as e:
            # Fallback if template file is missing (for initial testing without creating all files)
            return f"Prompt for {template_name} with context {kwargs}"

    def render_template(self, template_name: str, **kwargs) -> str:
        """Renders a code template."""
        return self.render_prompt(template_name, **kwargs)
