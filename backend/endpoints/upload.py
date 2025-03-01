from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
import uuid
from datetime import datetime

from services.pdf_processor import extract_text_from_pdf
from services.rag_pipeline import process_homework
from utils.file_helpers import save_upload_file, create_feedback_pdf
from config import UPLOAD_FOLDER

router = APIRouter()

@router.post("/upload/", summary="Upload marking criteria and homework PDFs")
async def upload_files(
    background_tasks: BackgroundTasks,
    marking_criteria: UploadFile = File(...),
    homework: UploadFile = File(...),
    student_name: str = Form(None),
    assignment_title: str = Form(None),
):
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Validate PDF files
    for pdf_file in [marking_criteria, homework]:
        if not pdf_file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"File {pdf_file.filename} is not a PDF")
    
    # Save uploaded files
    criteria_path = await save_upload_file(marking_criteria, f"{job_id}_criteria.pdf")
    homework_path = await save_upload_file(homework, f"{job_id}_homework.pdf")
    
    # Process PDFs in background
    background_tasks.add_task(
        process_submission,
        job_id,
        criteria_path,
        homework_path,
        student_name,
        assignment_title
    )
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Files uploaded successfully. Processing started.",
        "result_endpoint": f"/api/results/{job_id}"
    }

@router.get("/results/{job_id}", summary="Get processing results")
async def get_results(job_id: str):
    result_path = os.path.join(UPLOAD_FOLDER, f"{job_id}_feedback.pdf")
    
    if not os.path.exists(result_path):
        return {
            "job_id": job_id,
            "status": "processing",
            "message": "Processing is still ongoing. Please check back later."
        }
    
    return FileResponse(
        path=result_path,
        filename="feedback.pdf",
        media_type="application/pdf"
    )

async def process_submission(job_id, criteria_path, homework_path, student_name, assignment_title):
    try:
        # Extract text from PDFs
        criteria_text = extract_text_from_pdf(criteria_path)
        homework_text = extract_text_from_pdf(homework_path)
        
        # Process with RAG pipeline
        feedback, marks = process_homework(criteria_text, homework_text)
        
        # Generate feedback PDF
        feedback_path = os.path.join(UPLOAD_FOLDER, f"{job_id}_feedback.pdf")
        create_feedback_pdf(
            feedback_path,
            feedback,
            marks,
            student_name or "Unknown Student",
            assignment_title or "Untitled Assignment"
        )
    except Exception as e:
        # Log error and create error report
        print(f"Error processing submission {job_id}: {str(e)}") 