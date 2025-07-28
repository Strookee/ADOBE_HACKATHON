import fitz  # PyMuPDF
import json
import os
from sentence_transformers import SentenceTransformer, util
import torch
import datetime

def extract_text_chunks(pdf_path):
    """
    Extracts text from a PDF and divides it into meaningful chunks.
    For this implementation, each text block from PyMuPDF is treated as a chunk.
    """
    doc = fitz.open(pdf_path)
    chunks = []
    
    for page_num, page in enumerate(doc, start=1):
        # Using "blocks" maintains a good reading order and structure.
        blocks = page.get_text("blocks", sort=True)
        for block in blocks:
            # block[4] contains the text content of the block.
            block_text = block[4].strip()
            
            # We only consider blocks that contain text.
            if block_text:
                chunks.append({
                    "text": block_text,
                    "page": page_num,
                    "doc": os.path.basename(pdf_path)
                })
    return chunks

def process_documents(input_dir, output_dir):
    """
    Main function to process documents based on persona and job.
    """
    # Load the user's request from the JSON file.
    with open(os.path.join(input_dir, 'request.json'), 'r') as f:
        request = json.load(f)
    
    persona = request['persona']
    job_to_be_done = request['job_to_be_done']
    # Combine persona and job for a more effective search query.
    query = f"Persona: {persona}. Task: {job_to_be_done}"

    # Load the offline sentence transformer model from the local 'model' folder.
    print("Loading sentence transformer model...")
    model_path = 'model/'
    model = SentenceTransformer(model_path)
    print("Model loaded.")

    # Find all PDF files in the input directory and extract text chunks.
    all_chunks = []
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDF(s) to process.")
    for filename in pdf_files:
        pdf_path = os.path.join(input_dir, filename)
        all_chunks.extend(extract_text_chunks(pdf_path))

    # Convert the text chunks into numerical vectors (embeddings).
    print(f"Encoding {len(all_chunks)} text chunks...")
    chunk_texts = [chunk['text'] for chunk in all_chunks]
    chunk_embeddings = model.encode(chunk_texts, convert_to_tensor=True, show_progress_bar=True)
    
    # Convert the search query into an embedding.
    print("Encoding query...")
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Compute cosine similarity between the query and all text chunks.
    print("Calculating similarity scores...")
    cosine_scores = util.cos_sim(query_embedding, chunk_embeddings)[0]

    # Rank the chunks based on their similarity score in descending order.
    ranked_chunks = sorted(zip(cosine_scores, all_chunks), key=lambda x: x[0], reverse=True)

    # Prepare the output in the required JSON format.
    extracted_sections = []
    # Get the top 20 most relevant chunks.
    for i, (score, chunk) in enumerate(ranked_chunks[:20]): 
        extracted_sections.append({
            "document": chunk['doc'],
            "page_number": chunk['page'],
            # Use the first line of the chunk as a representative title.
            "section_title": chunk['text'].split('\n')[0], 
            "importance_rank": i + 1
        })
        
    output_data = {
        "metadata": {
            "input_documents": pdf_files,
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": datetime.datetime.now().isoformat()
        },
        "extracted_sections": extracted_sections
    }
    
    # Save the final output to a JSON file.
    output_path = os.path.join(output_dir, 'challenge1b_output.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
        
    print(f"Processing complete. Output saved to {output_path}")

if __name__ == "__main__":
    # These paths are where Docker will mount the volumes.
    INPUT_DIR = "/app/input"
    OUTPUT_DIR = "/app/output"
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    process_documents(INPUT_DIR, OUTPUT_DIR)