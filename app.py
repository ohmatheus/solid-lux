import os
import pandas as pd

from langchain_anthropic import ChatAnthropic

from modules import logger
from modules import extractor
from modules import cleaner

#---------------------------------------------------------------------------
def process_folder(folder_path, **kwargs):
    logger.info(f"Starting load and extraction of {folder_path} folder.")
    
    if not os.path.exists(folder_path):
        logger.error(f"Error: Folder {folder_path} does not exist.")
        return

    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]

    if not pdf_files:
        logger.info("No PDF files found.")
        return

    logger.info(f"Found {len(pdf_files)} PDF(s). Processing...\n")

    results = []

    for i, pdf in enumerate(pdf_files):
        logger.info(f"Processing {i+1}/{len(pdf_files)}.")
        pdf_path = os.path.join(folder_path, pdf)
        df = extractor.process_pdf(pdf_path, **kwargs)
        results.append(df)

    logger.info("Finished processing all PDFs.")
    return results

#---------------------------------------------------------------------------
def extract_from_foler(folder_path, **kwargs):
    results = process_folder(folder_path, **kwargs)
    
    if results is None:
        return
    
    iterator = iter(results)
    final_df = next(iterator)

    try:
        while True:
            df = next(iterator)
            final_df = pd.concat([final_df, df], ignore_index=True)
    except StopIteration:
        print("End of list reached")

    return final_df

#---------------------------------------------------------------------------
def main():
    logger.info("-------------- New App Session --------------")
    
    with open("./api_key.txt") as f:
        api_key=f.read() # TODO handle missing file

    anthropic_model = "claude-3-7-sonnet-20250219"
    logger.info(f"Using {anthropic_model} model.")

    llm = ChatAnthropic(model=anthropic_model,
                    temperature=0,
                    max_tokens=512,
                    timeout=None,
                    max_retries=2,
                    api_key=api_key)
    
    folder = './AllPDF'
    args = {
        "llm": llm,
    }
    
    raw_df = extract_from_foler(folder, **args)
    if raw_df is None:
        return
    raw_df.to_csv("extracted.csv", index=False)
    df_cleaned = cleaner.clean_and_format(raw_df)
    cleaned_file_path = "./extracted_cleaned.csv"
    df_cleaned.to_csv(cleaned_file_path, index=False)

    logger.info("-------------- End App Session --------------")
    input("Press Enter to exit...")


#---------------------------------------------------------------------------
if __name__ == "__main__":
    main()