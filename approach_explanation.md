# Approach for Round 1B: Persona-Driven Document Intelligence

Our solution for Round 1B tackles the challenge of extracting persona-driven insights from a collection of documents by implementing a robust, offline semantic search pipeline. The core of our methodology is built on transforming unstructured text into a meaningful, vector-based representation to accurately measure relevance against a user's specific needs.

## **Core Methodology**

Our approach can be broken down into three primary stages:

### **1. Text Extraction and Chunking**

The first step is to process the input PDF documents and extract their textual content in a structured manner. We utilize the `PyMuPDF` library for this task due to its efficiency and ability to preserve the logical reading order of the text. Instead of treating the entire document as a single block of text, we segment it into smaller, more coherent "chunks." In our implementation, each distinct text block identified by `PyMuPDF` is treated as an individual chunk. This method ensures that we have granular pieces of information—such as paragraphs, list items, or short statements—that can be independently evaluated for relevance. Each chunk is stored along with its source document and page number for easy reference.

### **2. Semantic Representation via Embeddings**

To understand the meaning behind the text, we convert both the extracted chunks and the user's query into high-dimensional vectors, or "embeddings." For this, we use the `sentence-transformers` library with the `all-MiniLM-L6-v2` model. This model was chosen for its excellent balance of performance and size, easily fitting within the hackathon's constraints.

Crucially, the model is downloaded and stored locally within our project. This ensures our solution is fully compliant with the offline execution requirement. The user's query is constructed by combining the provided "persona" and "job-to-be-done" descriptions, creating a comprehensive prompt that accurately reflects their informational needs.

### **3. Similarity Ranking**

With the query and all text chunks represented as vectors in the same semantic space, the final step is to quantify their relevance. We employ **cosine similarity** to measure the angular distance between the query vector and each chunk vector. A higher cosine similarity score indicates a closer semantic relationship.

The text chunks are then ranked in descending order based on their similarity scores. The top-ranked chunks are considered the most relevant sections for the user's request. This ranked list is then formatted into the final JSON output, providing a prioritized guide to the most important information scattered across the document collection. This entire pipeline provides a fast, efficient, and intelligent solution for persona-driven document analysis.