import logging
from dataclasses import dataclass
from typing import List

@dataclass
class Corpus:
    id: int
    name: str
    description: str
    dtProvision: str
    enabled: bool
    swapQenc: bool
    swapIenc: bool
    textless: bool
    encrypted: bool
    encoderId: str
    metadataMaxBytes: int
    faissIndexType: str
    # TODO Map these when I have an example
#    customDimensions: arr
#    filterAttributes:


@dataclass
class ListCorpusResponse:

    corpus: List[Corpus]
