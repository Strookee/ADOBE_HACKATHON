import fitz  # PyMuPDF
import json
import os
import collections

def get_text_styles(page):
    """Extracts font sizes and their frequencies from a page."""
    styles = collections.defaultdict(int)
    blocks = page.get_text("dict")
    for block in blocks["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                if "spans" in line:
                    for span in line["spans"]:
                        styles[round(span["size"])] += 1
    return styles

def get_heading_styles(styles, common_size):
    """Identifies potential heading font sizes."""
    # A heading is likely larger than the most common font size.
    # We can also add other rules, e.g., for boldness, if needed.
    heading_sizes = [size for size in styles if size > common_size]
    
    # Sort by size in descending order
    heading_sizes.sort(reverse=True)
    
    # Map the top 3 sizes to H1, H2, H3
    level_map = {}
    if len(heading_sizes) > 0:
        level_map[heading_sizes[0]] = "H1"
    if len(heading_sizes) > 1:
        level_map[heading_sizes[1]] = "H2"
    if len(heading_sizes) > 2:
        level_map[heading_sizes[2]] = "H3"
        
    return level_map

def extract_outline(pdf_path):
    """
    Extracts the title and a hierarchical outline (H1, H2, H3) from a PDF.
    """
    doc = fitz.open(pdf_path)
    
    # --- 1. Determine Base Font and Heading Styles ---
    full_doc_styles = collections.defaultdict(int)
    for page in doc:
        page_styles = get_text_styles(page)
        for size, count in page_styles.items():
            full_doc_styles[size] += count
            
    if not full_doc_styles:
        return {"title": "", "outline": []}

    # The most frequent font size is likely the body text
    common_size = max(full_doc_styles, key=full_doc_styles.get)
    
    # Determine which sizes correspond to H1, H2, H3
    heading_level_map = get_heading_styles(full_doc_styles, common_size)
    
    # --- 2. Extract Title and Headings ---
    outline = []
    doc_title = ""
    
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        
        # Simple title extraction: largest text on the first page
        if page_num == 1 and not doc_title:
             max_size = 0
             for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        if "spans" in line:
                            for span in line["spans"]:
                                if span["size"] > max_size:
                                    max_size = span["size"]
                                    doc_title = span["text"].strip()
        
        # Extract headings
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    # We assume a heading is a single line with uniform styling
                    if "spans" in line and len(line["spans"]) == 1:
                        span = line["spans"][0]
                        font_size = round(span["size"])
                        
                        if font_size in heading_level_map:
                            text = span["text"].strip()
                            # Avoid adding duplicates or very short, non-descriptive text
                            if text and len(text) > 2:
                                outline.append({
                                    "level": heading_level_map[font_size],
                                    "text": text,
                                    "page": page_num
                                })
                                
    return {
        "title": doc_title,
        "outline": outline
    }

def process_all_pdfs(input_dir, output_dir):
    """Processes all PDFs in the input directory and saves JSON to the output directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            json_output = extract_outline(pdf_path)
            
            output_filename = os.path.splitext(filename)[0] + ".json"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_output, f, ensure_ascii=False, indent=4)
            
            print(f"Processed {filename} -> {output_filename}")

if __name__ == "__main__":
    # These paths match the volume mounts in the docker run command
    INPUT_DIR = "/app/input"
    OUTPUT_DIR = "/app/output"
    process_all_pdfs(INPUT_DIR, OUTPUT_DIR)