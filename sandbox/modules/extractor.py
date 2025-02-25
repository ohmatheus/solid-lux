# Encapsulate all functions that transform pdf -> DataFrame


import pandas as pd

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.documents import Document

from langchain_community.document_loaders import PyPDFLoader

from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import TokenTextSplitter

from typing import Optional, List

from logger import logger

#---------------------------------------------------------------------------
class InsuranceExtraction_Rule(BaseModel):
    '''Different informations extracted from a company insurance's rule & rate files.'''
    # This doc-string is sent to the LLM as the description of the schema Person,
    # and it can help to improve extraction results.

    company_name: str = Field(
        description="The company that wrote this file."
    )
    min_premium: Optional[str] = Field(
        description="Minimum premium (The lowest amount the insurer will charge for coverage) in dollars, if there is multiple possible values, take the lowest.", 
        default=""
    )
    min_premium_comments: Optional[str] = Field(
        description="Minimum premium commentaries or additionnal informations"
    )
    policy_period: Optional[str] = Field(
        description="Policy period in month, if there is multiple possible values, take the lowest.", 
        default=""
    )
    policy_period_comments: Optional[str] = Field(
        description="Policy period commentaries or additionnal informations."
    )
    territory_factor_BI: Optional[str] = Field(
        description="The company's insurance territory factor for BI (Bodily Injury) insurance.", 
        default=""
    )

#---------------------------------------------------------------------------
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert extraction algorithm. "
            "Only extract relevant information from the text. "
            "If you do not know the value of an attribute asked to extract, "
            "return null for the attribute's value.",
        ),
        # Please see the how-to about improving performance with
        # reference examples.
        # MessagesPlaceholder('examples'),
        ("human", "{text}"),
    ]
)

#---------------------------------------------------------------------------
def split_pdf(file_path) -> List[Document]:
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    return pages


#---------------------------------------------------------------------------
def chunk_text(docs: List[Document]) -> List[str]:
    text_splitter = TokenTextSplitter(
        chunk_size=10000,
        chunk_overlap=20
        )
    text = " ".join(list(map(lambda page: page.page_content, docs)))
    text_processed = []
    text_processed += text_splitter.split_text(text)
    text_processed = [text for text in text_processed]
    return text_processed


#---------------------------------------------------------------------------
def extract(texts: List[str], llm) -> List[str]:
    total = len(texts)
    logger.info(f"Starting extraction on {total} chunks.")
    structured_llm_rule = llm.with_structured_output(schema=InsuranceExtraction_Rule, include_raw=False)
    extractor = prompt_template | structured_llm_rule
    try:
        extractions = extractor.batch(
            [{"text": text} for text in texts],
            {"max_concurrency": 5}
        )
    except Exception as e:
        logger.exception(f"An error occurred: {e}", exc_info=True)
        return []
    return extractions


#---------------------------------------------------------------------------
def convert_to_df(exts: List[str]) -> pd.DataFrame:
    extractions_dict = [extraction.__dict__ for extraction in exts]
    df = pd.DataFrame(extractions_dict)
    return df


#---------------------------------------------------------------------------
def process_pdf(file_path, llm, **kwargs):
    """Function to extract info from a PDF and return a DataFrame."""
    logger.info(f"Starting load and extraction of {file_path}")
    pages = split_pdf(file_path)
    text_processed = chunk_text(pages)
    extractions = extract(text_processed, llm)
    df = convert_to_df(extractions)
    return df