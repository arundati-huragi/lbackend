print("🔥 Topic Router Loaded")

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.core.database import get_db
from app.db.models import IEMSCourses, IEMSection, CudosTopic
from .topic_schema import (
    CourseListRequest,
    TopicSectionListRequest,
    TopicCreateRequest,
    TopicListRequest
)

router = APIRouter()


# ==============================
# API 1 – Course List
# ==============================
@router.post("/course_list")
def get_course_list(request: CourseListRequest, db: Session = Depends(get_db)):

    courses = db.query(IEMSCourses).filter(
        IEMSCourses.program_id == request.curriculum_id,
        IEMSCourses.semester == request.term_id
    ).all()

    return courses


# ==============================
# API 2 – Section List
# ==============================
@router.post("/section_list")
def get_section_list(request: TopicSectionListRequest, db: Session = Depends(get_db)):

    sections = db.query(IEMSection).filter(
        IEMSection.pgm_id == request.program_id,
        IEMSection.semester_id == request.semester
    ).all()

    return sections


# ==============================
# API 3 – Import Topic (CREATE)
# ==============================
from sqlalchemy.exc import IntegrityError

@router.post("/import_topic")
def import_topic(request: TopicCreateRequest, db: Session = Depends(get_db)):

    try:
        new_topic = CudosTopic(
            topic_code=request.topic_code,
            topic_title=request.topic_title,
            topic_content=request.topic_content,
            academic_batch_id=request.academic_batch_id,
            semester_id=request.semester_id,
            course_id=request.course_id,
            created_by=request.created_by,
            created_date=date.today()
        )

        db.add(new_topic)
        db.commit()
        db.refresh(new_topic)

        return {"message": "Topic imported successfully"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid academic_batch_id / semester_id / course_id"
        )

# ==============================
# API 4 – Topic List (READ)
# ==============================
@router.post("/topic_list")
def topic_list(request: TopicListRequest, db: Session = Depends(get_db)):

    topics = db.query(CudosTopic).filter(
        CudosTopic.academic_batch_id == request.academic_batch_id,
        CudosTopic.semester_id == request.semester_id,
        CudosTopic.course_id == request.course_id
    ).all()

    return topics


# ==============================
# API 5 – Update Topic (UPDATE)
# ==============================
@router.put("/update_topic/{topic_id}")
def update_topic(topic_id: int, request: TopicCreateRequest, db: Session = Depends(get_db)):

    topic = db.query(CudosTopic).filter(
        CudosTopic.topic_id == topic_id
    ).first()

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    try:
        topic.topic_code = request.topic_code
        topic.topic_title = request.topic_title
        topic.topic_content = request.topic_content
        topic.academic_batch_id = request.academic_batch_id
        topic.semester_id = request.semester_id
        topic.course_id = request.course_id
        topic.modified_by = request.created_by
        topic.modified_date = date.today()

        db.commit()
        db.refresh(topic)

        return {"message": "Topic updated successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ==============================
# API 6 – Delete Topic (DELETE)
# ==============================
@router.delete("/delete_topic/{topic_id}")
def delete_topic(topic_id: int, db: Session = Depends(get_db)):

    topic = db.query(CudosTopic).filter(
        CudosTopic.topic_id == topic_id
    ).first()

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    try:
        db.delete(topic)
        db.commit()
        return {"message": "Topic deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))