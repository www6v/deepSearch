import json
from json.decoder import JSONDecodeError
import openai
from config import config
from prompts import SYSTEM_PROMPT_REPORT_STRUCTURE, SYSTEM_PROMPT_FIRST_SEARCH, SYSTEM_PROMPT_FIRST_SUMMARY, SYSTEM_PROMPT_REFLECTION, \
    SYSTEM_PROMPT_REPORT_FORMATTING, SYSTEM_PROMPT_REFLECTION_SUMMARY
from state import State, Paragraph, Research, Search
from utils import clean_json_tags, remove_reasoning_from_output, clean_markdown_tags


class ReportStructureAgent:

    def __init__(self, query: str):

        self.openai_client = openai.OpenAI(
            api_key=config.SAMBANOVA_API_KEY,
            base_url=config.SAMBANOVA_BASE_URL
        )
        self.query = query

    def run(self) -> str:

        response = self.openai_client.chat.completions.create(
            model=config.LLM_REASONING,
            messages=[{"role": "system", "content": SYSTEM_PROMPT_REPORT_STRUCTURE},
                      {"role":"user","content": self.query}]
        )
        return response.choices[0].message.content

    def mutate_state(self, state: State) -> State:

        report_structure = self.run()
        report_structure = remove_reasoning_from_output(report_structure)
        report_structure = clean_json_tags(report_structure)

        report_structure = json.loads(report_structure)

        for paragraph in report_structure:
            state.paragraphs.append(Paragraph(title=paragraph["title"], content=paragraph["content"]))

        return state    


class FirstSearchAgent:

    def __init__(self):

        self.openai_client = openai.OpenAI(
            api_key=config.SAMBANOVA_API_KEY,
            base_url=config.SAMBANOVA_BASE_URL
        )

    def run(self, message) -> str:

        response = self.openai_client.chat.completions.create(
            model=config.LLM_REGULAR,
            messages=[{"role": "system", "content": SYSTEM_PROMPT_FIRST_SEARCH},
                      {"role":"user","content": message}]
        )

        response = remove_reasoning_from_output(response.choices[0].message.content)
        response = clean_json_tags(response)

        response = json.loads(response)

        return response
    

class FirstSummaryAgent:

    def __init__(self):

        self.openai_client = openai.OpenAI(
            api_key=config.SAMBANOVA_API_KEY,
            base_url=config.SAMBANOVA_BASE_URL
        )

    def run(self, message) -> str:

        response = self.openai_client.chat.completions.create(
            model=config.LLM_REGULAR,
            messages=[{"role": "system", "content": SYSTEM_PROMPT_FIRST_SUMMARY},
                      {"role":"user","content": message}]
        )
        return response.choices[0].message.content

    def mutate_state(self, message: str, idx_paragraph: int, state: State) -> State:

        summary = self.run(message)
        summary = remove_reasoning_from_output(summary)
        summary = clean_json_tags(summary)
        
        try:
            summary = json.loads(summary)
        except JSONDecodeError:
            summary = {"paragraph_latest_state": summary}

        state.paragraphs[idx_paragraph].research.latest_summary = summary["paragraph_latest_state"]

        return state
    

class ReflectionAgent:

    def __init__(self):

        self.openai_client = openai.OpenAI(
            api_key=config.SAMBANOVA_API_KEY,
            base_url=config.SAMBANOVA_BASE_URL
        )

    def run(self, message) -> str:

        response = self.openai_client.chat.completions.create(
            model=config.LLM_REGULAR,
            messages=[{"role": "system", "content": SYSTEM_PROMPT_REFLECTION},
                      {"role":"user","content": message}]
        )

        response = remove_reasoning_from_output(response.choices[0].message.content)
        response = clean_json_tags(response)
        response = json.loads(response)

        return response
    

class ReflectionSummaryAgent:

    def __init__(self):

        self.openai_client = openai.OpenAI(
            api_key=config.SAMBANOVA_API_KEY,
            base_url=config.SAMBANOVA_BASE_URL
        )

    def run(self, message) -> str:

        response = self.openai_client.chat.completions.create(
            model=config.LLM_REGULAR,
            messages=[{"role": "system", "content": SYSTEM_PROMPT_REFLECTION_SUMMARY},
                      {"role":"user","content": message}]
        )
        return response.choices[0].message.content

    def mutate_state(self, message: str, idx_paragraph: int, state: State) -> State:

        summary = self.run(message)
        summary = remove_reasoning_from_output(summary)
        summary = clean_json_tags(summary)

        try:
            summary = json.loads(summary)
        except JSONDecodeError:
            summary = {"updated_paragraph_latest_state": summary}

        state.paragraphs[idx_paragraph].research.latest_summary = summary["updated_paragraph_latest_state"]

        return state
    

class ReportFormattingAgent:

    def __init__(self):

        self.openai_client = openai.OpenAI(
            api_key=config.SAMBANOVA_API_KEY,
            base_url=config.SAMBANOVA_BASE_URL
        )

    def run(self, message) -> str:

        response = self.openai_client.chat.completions.create(
            model=config.LLM_REASONING,
            messages=[{"role": "system", "content": SYSTEM_PROMPT_REPORT_FORMATTING},
                      {"role":"user","content": message}]
        )
        summary = response.choices[0].message.content
        summary = remove_reasoning_from_output(summary)
        summary = clean_markdown_tags(summary)
        
        return summary
