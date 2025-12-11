from liquid import CachingFileSystemLoader, Environment


class PromptLoader:
    def __init__(self, prompt_dir: str = "./prompt"):
        self.prompt_dir = prompt_dir
        self.env = Environment(loader=CachingFileSystemLoader(self.prompt_dir))

    def load_prompt(self, prompt_name: str) -> str:
        template = self.env.get_template(prompt_name)
        return template.render()

    def load_prompt_with_context(self, prompt_name: str, context: dict) -> str:
        template = self.env.get_template(prompt_name)
        return template.render(**context)
