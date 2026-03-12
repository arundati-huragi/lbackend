from fastapi import APIRouter, Depends, HTTPException, Body,UploadFile, File, Form
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import os
from app.core.database import get_db
from app.api.v1.material.material_schema import *
from app.db.models import *

router = APIRouter()

@router.post("/create_material")
def create_material(
    academic_batch_id: int = Form(...),
    semester_id: int = Form(...),
    course_id: int = Form(...),
    section_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(None),
    created_by: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # ---------- FILE TYPE VALIDATION ----------
    allowed_types = ["pdf","doc","docx","ppt","pptx"]

    file_ext = file.filename.split(".")[-1]

    if file_ext not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")


    # ---------- FILE SAVE ----------
    upload_folder = "uploads/materials"

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    file_path = f"{upload_folder}/{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())


    # ---------- DB INSERT ----------
    material = LMSCourseMaterialUpload(
    document_name=title,
    file_name=file.filename,
    docment_url=file_path,
    description=description,
    academic_batch_id=academic_batch_id,
    semester_id=semester_id,
    crs_id=course_id,
    section_ids=str(section_id),
    topic_ids=None,
    created_by=created_by,
    update_cnt=0
    )

    db.add(material)
    db.commit()
    db.refresh(material)

    return {
        "status": True,
        "message": "Material uploaded successfully"
    }


@router.post("/material_list")
def material_list(request: MaterialListRequest, db: Session = Depends(get_db)):

    materials = db.query(LMSCourseMaterialUpload).filter(
        LMSCourseMaterialUpload.academic_batch_id == request.academic_batch_id,
        LMSCourseMaterialUpload.semester_id == request.semester_id,
        LMSCourseMaterialUpload.crs_id == request.course_id,
        LMSCourseMaterialUpload.section_ids.contains(str(request.section_id))    ).all()

    return materials


@router.post("/student_list")
def student_list(section_id: int = Body(...), db: Session = Depends(get_db)):
    students = db.query(IEMSUsers).filter(
    IEMSUsers.is_student == 1
).all()

    return [
        {
            "value": s.id,
            "label": f"{s.first_name} {s.last_name}"
        }
        for s in students
    ]

@router.post("/share_material")
def share_material(request: ShareMaterialRequest, db: Session = Depends(get_db)):

    for student_usn in request.student_usns:

        mapping = LMSMapShareMaterialsToStudent(
            ssd_id=None,
            mat_id=request.material_id,
            academic_batch_id=request.academic_batch_id,
            section_id=request.section_id,
            student_usn=student_usn
        )

        db.add(mapping)

    db.commit()

    return {
        "status": True,
        "message": "Material shared successfully"
    }

@router.get("/download_material/{mat_id}")
def download_material(mat_id: int, db: Session = Depends(get_db)):

    material = db.query(LMSCourseMaterialUpload).filter(
        LMSCourseMaterialUpload.mat_id == mat_id
    ).first()

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    return FileResponse(material.docment_url, filename=material.file_name)