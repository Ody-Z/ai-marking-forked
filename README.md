## File Descriptions
### Backend
app.py:
The entry point for your FastAPI application. It initializes the server, loads configurations, and registers API routes (like the upload endpoint).

config.py:
Holds configuration settings such as API keys, database endpoints (for Pinecone), file paths, and other environment-specific settings.

endpoints/upload.py:
Defines the REST endpoint(s) to receive file uploads (both marking criteria and student homework). This endpoint triggers the processing pipeline.

models/__init__.py:
Optional placeholder for data models if you decide to extend your MVP to include more structured data in the future.

services/pdf_processor.py:
Contains logic to extract text content from the uploaded PDF files. This text is used for further analysis and retrieval.

services/llm_service.py:
Provides a wrapper around your chosen LLM API. It constructs the prompt (using inputs from the RAG pipeline) and retrieves generated feedback and marks.

services/rag_pipeline.py:
Implements a basic Retrieval Augmented Generation workflow using LangChain. It retrieves relevant context from Pinecone (using the pinecone_service) and merges it with the PDF content to create a rich prompt for the LLM.

services/pinecone_service.py:
Manages interactions with the Pinecone vector database. This includes indexing, storing, and querying vector embeddings that represent content from the marking criteria or previous assignments.

utils/file_helpers.py:
Provides utility functions for managing file uploads, saving temporary files, and any necessary format conversions.

requirements.txt:
Lists all Python dependencies, such as FastAPI, LangChain, the Pinecone client library, PDF processing libraries (e.g., PyPDF2), and PDF generation libraries (e.g., reportlab).

Dockerfile (backend):
Defines the instructions for containerizing your backend service, ensuring that all dependencies are installed and the FastAPI app is served correctly.

README.md (backend):
Includes setup instructions, a description of the backend functionality, and how to run tests and start the service.

### Frontend
index.html:
A basic HTML page that provides a form for uploading the marking criteria and student homework PDFs.

app.js:
Handles the front-end logic to capture file uploads, send them to the backend API, and display processing results or feedback status.

styles.css:
Provides basic styling to enhance the look of the upload form and any messages shown to the user.

README.md (frontend):
Contains instructions for setting up and running the frontend, including any dependencies or build steps.

### Root-Level Files
docker-compose.yml:
Orchestrates both backend and frontend containers, enabling you to run the full MVP locally with a single command.

.env:
Stores environment variables, such as API keys for the LLM service, Pinecone configuration details, and other sensitive settings, to keep them out of source control.

README.md (project-root):
Provides an overall project overview, high-level architecture description, setup instructions, and guides on how to run and deploy the MVP.
