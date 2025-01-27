from typing import Optional
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.outputs import Generation
from langchain_core.utils.pydantic import (
    PYDANTIC_MAJOR_VERSION,
)
import re


class PydanticThoughtParser(PydanticOutputParser):
    """Parse an output using a pydantic model and automatically adds the `think` property to the output."""

    def build_thought_field(self):
        """Dynamically add a 'thought' field to the pydantic model."""

        if PYDANTIC_MAJOR_VERSION == 2:
            self.pydantic_object.__annotations__["thought"] = (Optional[str], None)
            self.pydantic_object.model_rebuild()
        else:  # pydantic v1
            self.pydantic_object.update_forward_refs(thought=(Optional[str], None))

    def parse_result(self, result: list[Generation], *, partial: bool = False):
        self.build_thought_field()

        pattern = r"<think>(.*?)</think>"
        extracted_thoughts = re.findall(pattern, result[0].text, re.DOTALL)

        if extracted_thoughts:
            extracted_thought = extracted_thoughts[0]
            # remove the think tag, since it breaks the json parsing
            updated_text = re.sub(pattern, "", result[0].text, flags=re.DOTALL)
            result[0].text = updated_text
        else:
            extracted_thought = None

        parsed_object = super().parse_result(result, partial=partial)
    
        if extracted_thought:
            parsed_object.thought = extracted_thought  # type: ignore
    
        return parsed_object
