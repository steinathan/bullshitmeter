from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatLiteLLM

from langchain_core.output_parsers import PydanticOutputParser
from urllib.parse import urlparse

from langchain_community.document_loaders import WebBaseLoader
import logging

from pydantic_thought_parser import PydanticThoughtParser


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvalidInputException(ValueError):
    pass


class BSLLMOutput(BaseModel):
    score: int = Field(
        1, description="The score of how 'bullshit' it appears to be", ge=0, lt=11
    )
    explanation: str = Field(
        "",
        description="A detailed thoughtful explanation of why you think its 'bullshit'",
    )

    class Config:
        extra = "allow"


class BSServiceConfig(BaseModel):
    model: str = "ollama/deepseek-r1"
    api_key: str | None = None
    api_base: str | None = ""


class BSService:
    def __init__(self, config: BSServiceConfig):
        self.config = config
        self.model = ChatLiteLLM(
            model=self.config.model,
            api_key=self.config.api_key,
            api_base=self.config.api_base,
        )

    def scrape_url(self, url, n_docs=5) -> str:
        logger.debug(f"scrapping url: {url}")

        loader = WebBaseLoader(url)
        loader.requests_kwargs = {"verify": False}
        docs = loader.load()

        docs = docs[:n_docs]
        content = " ".join(doc.page_content for doc in docs)

        return content

    def calculate_bullshit(self, maybe_text_or_url) -> BSLLMOutput:
        text = None

        if self.is_url(maybe_text_or_url):
            text = self.scrape_url(maybe_text_or_url)
        else:
            text = maybe_text_or_url

        if not text:
            raise InvalidInputException("inconsistency violation")

        data = self._calculate_bullshit(text)
        return data

    def _calculate_bullshit(self, text) -> BSLLMOutput:
        system_prompt = """
You are the Bullshit Analyzer Supreme, a no-nonsense, all-seeing expert trained to detect and rate the level of 'bullshit' in any user-provided text, whether it's a tweet, post, website content, marketing pitch, political speech, or overly dramatic self-help quote. 

Your style is as irreverent and unfiltered as the world of *Farzar*—equal parts sarcastic wit, absurd humor, and ruthless honesty. Your mission: to critically analyze the text, call out galactic-level nonsense, and expose unrealistic expectations or dubious claims with brutal yet entertaining precision.

Provide a score from 0 to 9 based on how 'bullshit' the text appears to be, with:
- 0: "Absolutely no bullshit detected. This is the unshakable truth, like gravity on a well-regulated space station."
- 10: "Maximum bullshit. This text reeks of unrealistic expectations and should be jettisoned into a black hole immediately."

In addition to the score, provide a hilariously blunt, detailed explanation for your judgment. Use commentary to break down the flaws, exaggerations, or questionable elements of the text. 
Your analysis should leave no room for doubt—whether you're validating a rare nugget of honesty or gleefully dismantling an intergalactic dumpster fire of nonsense.

{format_instructions}
"""
        user_prompt = "{text}"

        parser = PydanticThoughtParser(pydantic_object=BSLLMOutput)
        prompt = ChatPromptTemplate(
            [("system", system_prompt), ("user", user_prompt)]
        ).partial(format_instructions=parser.get_format_instructions())

        chain = prompt | self.model | parser

        result = chain.invoke({"text": text})
        return result

    def is_url(self, maybe_text_or_url) -> bool:
        try:
            result = urlparse(maybe_text_or_url)
            if result.scheme:
                return True
            return False
        except Exception:
            return False
