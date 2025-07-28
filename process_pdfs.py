#!/usr/bin/env python3  
import os  
import json  
from pathlib import Path  
from mineru.cli.common import do_parse, read_fn  
  
def process_pdfs():  
    input_dir = Path("/app/input")  
    output_dir = Path("/app/output")  
      
    # Find all PDF files  
    pdf_files = list(input_dir.glob("*.pdf"))  
      
    if not pdf_files:  
        print("No PDF files found in /app/input")  
        return  
      
    for pdf_file in pdf_files:  
        try:  
            print(f"Processing {pdf_file.name}...")  
              
            # Read PDF  
            pdf_bytes = read_fn(pdf_file)  
              
            # Process with your modified MinerU  
            do_parse(  
                output_dir=str(output_dir),  
                pdf_file_names=[pdf_file.stem],  
                pdf_bytes_list=[pdf_bytes],  
                p_lang_list=['en'],  
                backend='pipeline',  
                parse_method='auto',  
                formula_enable=False,  # Disabled as you removed formula models  
                table_enable=False,    # Disabled as you removed table models  
                f_dump_content_list=True,  
                f_make_md_mode='CONTENT_LIST'  
            )  
              
            # Move and rename the content list file to match requirements  
            content_list_file = output_dir / pdf_file.stem / "auto" / f"{pdf_file.stem}_content_list.json"  
            if content_list_file.exists():  
                target_file = output_dir / f"{pdf_file.stem}.json"  
                content_list_file.rename(target_file)  
                print(f"Generated {target_file.name}")  
            else:  
                print(f"Warning: Content list file not found for {pdf_file.name}")  
              
        except Exception as e:  
            print(f"Error processing {pdf_file.name}: {e}")  
  
if __name__ == "__main__":  
    process_pdfs()