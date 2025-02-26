# Encapsulate all functions that transform pdf -> DataFrame

import pandas as pd

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.documents import Document

from langchain_community.document_loaders import PyPDFLoader

from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import TokenTextSplitter

from typing import Optional, List

from modules.logger_mod import logger

__all__ = ["public_function", "PUBLIC_VAR"]

#---------------------------------------------------------------------------
# In the current form, those attributes will also be the dataframe headers
class _InsuranceExtraction_Rule(BaseModel):
    '''Different informations extracted from a company insurance's rule & rate files.'''
    # This doc-string is sent to the LLM as the description of the schema,
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
    supp_fee_policy: Optional[str] = Field(
        description="Additionnal fee per policy.",
        default=""
    )
    coverage_BI: Optional[str] = Field(
        description=f"""Categorical value required. If the compagny include BI (Bodily Injury) coverage in the formula. 
        Select only between [mandatory, optionnal, none]""", 
    )
    coverage_PD: Optional[str] = Field(
        description=f"""Categorical value required. If the compagny include PD (Property Damage) coverage in the formula. 
        Select only between [mandatory, optionnal, none]""", 
    )
    coverage_MED: Optional[str] = Field(
        description=f"""Categorical value required. If the compagny include MED (Medical Payments) coverage in the formula. 
        Select only between [mandatory, optionnal, none]""", 
    )
    coverage_UM_UIMBI: Optional[str] = Field(
        description=f"""Categorical value required. If the compagny include UM/UIMBI (Uninsured/Underinsured Motorists Bodily Injury) coverage in the formula. 
        Select only between [mandatory, optionnal, none]""", 
    )
    coverage_UMPD: Optional[str] = Field(
        description=f"""Categorical value required. If the compagny include UMPD (Uninsured/Underinsured Motorists Property Damage) coverage in the formula. 
        Select only between [mandatory, optionnal, none]""", 
    )
    coverage_COMP: Optional[str] = Field(
        description=f"""Categorical value required. If the compagny include COMP (Comprehensive) coverage in the formula. 
        Select only between [mandatory, optionnal, none]""", 
    )
    coverage_COLL: Optional[str] = Field(
        description=f"""Categorical value required. If the compagny include COLL (Collision) coverage in the formula. 
        Select only between [mandatory, optionnal, none]""", 
    )
    coverage_GAP: Optional[str] = Field(
        description=f"""Categorical value required. If the compagny include GAP (Auto Loan/Lease Gap Coverage) coverage in the formula. 
        Select only between [mandatory, optionnal, none]""", 
    )

#---------------------------------------------------------------------------
_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert extraction algorithm. "
            "Only extract relevant information from the text. "
            "If you do not know the value of an attribute asked to extract, "
            "Try to deduce it or "
            "return null for the attribute's value.",
        ),
        # Please see the how-to about improving performance with
        # reference examples.
        # MessagesPlaceholder('examples'),
        ("human", "{text}"),
    ]
)

#---------------------------------------------------------------------------
def _split_pdf(file_path) -> List[Document]:
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    return pages


#---------------------------------------------------------------------------
def _chunk_text(docs: List[Document]) -> List[str]:
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
def _extract(texts: List[str], llm) -> List[str]:
    total = len(texts)
    logger.info(f"Starting extraction on {total} chunks.")
    structured_llm_rule = llm.with_structured_output(schema=_InsuranceExtraction_Rule, include_raw=False)
    extractor = _prompt_template | structured_llm_rule
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
def _convert_to_df(exts: List[str]) -> pd.DataFrame:
    extractions_dict = [extraction.__dict__ for extraction in exts]
    df = pd.DataFrame(extractions_dict)
    return df


#---------------------------------------------------------------------------
def process_pdf(file_path, llm, **kwargs):
    """Function to extract info from a PDF and return a DataFrame."""
    logger.info(f"Starting load and extraction of {file_path}")
    pages = _split_pdf(file_path)
    text_processed = _chunk_text(pages)
    extractions = _extract(text_processed, llm)
    df = _convert_to_df(extractions)
    return df