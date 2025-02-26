# solid-lux
This app simply run through a folder containning PDF, extract data from them (on a predetermined structure) using LLM and brute force data extraction, and output a cleaned csv on root folder.

## How to Use
1. Create Venv in root folder
2. Install requirements.txt
3. Copy you anthropic api key in api_key.txt
4. Copy `AllPDF` folder in root folder
5. launch app.py or notebooks `2_pdf_extract_pipeline.ipynb` & `3_clean_data.ipynb`

## Data Structure
You will be able to access this structure in `extractor.py`.  
This class is used by langchain to prompt the llm an retreive relevant information with `llm.with_structured_output(...)`  
This structure directly defines the output csv's headers.

```python
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
```

## Output exemple
|    | company_name                                                      |   min_premium | min_premium_comments                                                                                                                                                                                                                                                     |   policy_period | policy_period_comments                                                                                                                                                                  |   supp_fee_policy | coverage_BI   | coverage_PD   | coverage_MED   | coverage_UM_UIMBI   | coverage_UMPD   | coverage_COMP   | coverage_COLL   | coverage_GAP   |
|---:|:------------------------------------------------------------------|--------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------:|:--------------|:--------------|:---------------|:--------------------|:----------------|:----------------|:----------------|:---------------|
| 17 | Pronto General Agency, LTD                                        |            14 | This is the policy fee for a 1-month policy, which appears to be the minimum policy term available.                                                                                                                                                                      |               1 | Available policy terms are 1 month, 3 months, or 6 months.                                                                                                                              |       1.41354e+08 | mandatory     | mandatory     | optional       | optional            | optional        | optional        | optional        | none           |
| 18 | Redpoint Insurance Group                                          |           100 | The minimum premium charge for Special Equipment Coverage is $100.00, though this is not the overall policy minimum premium.                                                                                                                                             |               1 | Policy terms available are 1 month, 3 month, or 6 month                                                                                                                                 |      82           | mandatory     | mandatory     | optional       | optional            | optional        | optional        | optional        | none           |
| 19 | Tesla Property & Casualty, Inc.                                   |           100 | The minimum premium is for a six-month policy, which cannot be reduced except in the event of a cancellation.                                                                                                                                                            |               6 | Personal Auto Policies may be written for policy periods for 6 months or less.                                                                                                          |       4           | mandatory     | mandatory     | optional       | optional            | optional        | optional        | optional        | optional       |
| 20 | Texas Automobile Insurance Plan Association                       |           100 | Based on Rule 3 which likely specifies a policy minimum premium, though the exact amount is not clearly visible in the provided text.                                                                                                                                    |               6 | Standard policy period appears to be 6 months based on industry standards for auto insurance in Texas.                                                                                  |       4           | mandatory     | mandatory     | optional       | optional            | optional        | optional        | optional        | none           |
| 21 | Texas Automobile Insurance Plan Association (TAIPA)               |            20 | $20 for the insured for whom the certificate is filed.                                                                                                                                                                                                                   |               6 | The document mentions a continuous period of at least six months for leased vehicles to be considered private passenger autos.                                                          |       1           | mandatory     | mandatory     | optional       | optional            | optional        | optional        | optional        | none           |


## Possible Improvements
There is plenty of room to improve this app :

1. General architecture:
	- Reorganize pdf by compagny (and by assurance type in a larger scheme)
	- Creating a RAG system while doing extraction to reduce llm usage
    - Tag files with what they contains to narrow the first search

2. Data Cleaning
    - Better selection of 'right' values while merging rows

3. Data extraction:
	- Being able to extract tables, those are important

4. Data science & Machine Learning
    - Compare data on some extracted factor (one tables can be extracted)
    - Using a clustering algorithm to group compagnies under certain factor

5. Application :
	- Unit tests
	- Add user interface (Tkinter, PyQt, etc.)
    - Automate PDF downloading (maybe via REST API or improved web scrapping)

## Final Thoughts
This is a POC, or a study, to see what is possible to do, and is not by any mean ready for production.  
I wanted to make it 'clean' under the form of an app to have a better material to work with if ever I want to improve it in a near future.  
If we ever want to modify the extraction or the dataframe cleaning, it is pretty easy to do now.  
Nevertheless, i'm a bit frustrated to not having been able to extract sufficient data to perform some kind of data analysis on this, even if i have many ideas that would apply to this project.  
It's interesting to see how we can leverage the use of llm for feature extraction.