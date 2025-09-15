from fastapi import APIRouter, HTTPException
from app.services.ia_service import process_document, get_result

router = APIRouter()