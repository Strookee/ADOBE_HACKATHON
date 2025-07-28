# Adobe Hackathon 2025 - Round 1 Submission

This repository contains the complete solutions for both Round 1A and Round 1B of the "Connecting the Dots" challenge. Each solution is containerized with Docker for easy and consistent evaluation.

---

## Prerequisites

-   **Docker**: Ensure Docker Desktop is installed and running on your system.

---

## Project Structure

-   `process_pdf.py`: The Python script for the Round 1A solution.
-   `process_1b.py`: The Python script for the Round 1B solution.
-   `Dockerfile.1a`: The Dockerfile used to build and run the Round 1A solution.
-   `Dockerfile.1b`: The Dockerfile used to build and run the Round 1B solution.
-   `approach_explanation.md`: A detailed explanation of the methodology for Round 1B.
-   `model/`: A local directory containing the offline `all-MiniLM-L6-v2` sentence transformer model.

---

## **Round 1A: Understand Your Document**

[cite_start]This solution extracts a structured outline (Title, H1, H2, H3) from a given PDF document. [cite: 30]

### **Approach**
[cite_start]The script utilizes the `PyMuPDF` library to perform a structural analysis of the PDF. [cite: 89, 90] [cite_start]It determines the body text font size by frequency and classifies any larger text as a heading. [cite: 89] These headings are then sorted by size to assign H1, H2, and H3 levels. [cite_start]This heuristic-based approach is designed to be fast, efficient, and fully compliant with the offline, CPU-only constraints. [cite: 58, 60]

### **How to Build and Run (1A)**
1.  **Build the Docker Image:**
    [cite_start]Use the following command to build the image using the specific Dockerfile for Round 1A. [cite: 93]
    ```bash
    docker build --platform linux/amd64 -f Dockerfile.1a -t pdf-extractor:latest .
    ```

2.  **Run the Container:**
    Place your test PDF(s) in the `input` folder. Run the container with the following command. [cite_start]It will automatically process all PDFs and save the JSON results to the `output` folder. [cite: 69]
    ```bash
    docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none pdf-extractor:latest
    ```

---

## **Round 1B: Persona-Driven Document Intelligence**

[cite_start]This solution analyzes a collection of documents to extract and rank sections that are most relevant to a specific user persona and their stated goal. [cite: 109]

### **Approach**
[cite_start]The system implements a semantic search pipeline designed for offline execution: [cite: 155]
1.  **Text Extraction**: PDF documents are broken down into manageable text chunks using `PyMuPDF`.
2.  **Semantic Representation**: A pre-trained `SentenceTransformer` model (`all-MiniLM-L6-v2`) is used to convert the text chunks and the user query into numerical vectors (embeddings). [cite_start]The model is stored locally to ensure offline functionality. [cite: 152]
3.  **Similarity Ranking**: Cosine similarity is calculated between the user's query vector and each text chunk's vector. The chunks are then ranked by their similarity score to identify and prioritize the most relevant information across all documents.

### **How to Build and Run (1B)**
1.  **Build the Docker Image:**
    [cite_start]Use the following command to build the image using the specific Dockerfile for Round 1B. [cite: 93]
    ```bash
    docker build --platform linux/amd64 -f Dockerfile.1b -t pdf-persona-extractor:latest .
    ```

2.  **Run the Container:**
    Ensure the `input` folder contains your test PDFs and a `request.json` file. Run the container with the following command.
    ```bash
    docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none pdf-persona-extractor:latest
    ```
    The final ranked output will be saved as `challenge1b_output.json` in the `output` folder.

---

### **Libraries Used**

* **PyMuPDF**: For high-performance PDF text extraction.
* **sentence-transformers**: For generating text embeddings.
* **torch**: A core dependency for the `sentence-transformers` library.
* **scikit-learn**: Used for its utility functions.