from .LlmTool import LlmTool
from typing import Annotated

class DirListing(LlmTool):
    name = "dir_listing"
    description = "Returns the list of files and dirs in the root directory"


    def execute(self, path: Annotated[str, "Directory relative to the project root"] = ".",) -> list[str]:
        return []