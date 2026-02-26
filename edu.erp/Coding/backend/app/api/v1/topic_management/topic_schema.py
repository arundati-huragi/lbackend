from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel

class CourseListRequest(BaseModel):
    curriculum_id: int
    term_id: int


class TopicSectionListRequest(BaseModel):
    program_id: int
    semester: int


class ImportTopicRequest(BaseModel):
    topic_code: Optional[str]
    topic_title: str
    topic_content: Optional[str]
    academic_batch_id: int
    semester_id: int
    course_id: int
    created_by: int

class TopicCreateRequest(BaseModel):
    topic_code: str
    topic_title: str
    topic_content: str
    academic_batch_id: int
    semester_id: int
    course_id: int
    created_by: int
    
class TopicListRequest(BaseModel):
    academic_batch_id: int
    semester_id: int
    course_id: int

