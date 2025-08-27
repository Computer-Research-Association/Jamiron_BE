from typing import List, Dict, Any
from sqlalchemy.orm import Session
from src.app.classifier.methods.rule import RuleBasedClassifier
from src.app.classifier.methods.ml import MLClassifier
from src.app.model import UserSyllabusData, Syllabus

def get_user_syllabuses(db: Session, user_id: str, year: str, semester: str) -> List[Dict[str, Any]]:
    user_courses = db.query(UserSyllabusData).filter(
        UserSyllabusData.user_id == user_id,
        UserSyllabusData.year == year,
        UserSyllabusData.semester == semester
    ).all()

    if not user_courses:
        return []

    results = []
    for course in user_courses:
        matching_syllabus = db.query(Syllabus).filter(
            Syllabus.class_code == course.class_code,
            Syllabus.year == course.year,
            Syllabus.semester == course.semester
        ).first()

        if matching_syllabus:
            results.append({
                "user_id": course.user_id,
                "class_code": course.class_code,
                "year": course.year,
                "semester": course.semester,
                "professor_name": course.professor_name,

                "syllabus_class_name": matching_syllabus.class_name,
                "syllabus_description": matching_syllabus.description,
                "syllabus_objectives": matching_syllabus.objectives,
                "syllabus_schedule": matching_syllabus.schedule
            })
    print ("봐야한다", results)
    return results


def classify_with_rule_and_ml(file_data_list, db=None, syllabus_list=None):
    """
    Rule 기반 → ML 기반 분류
    syllabus_list: MLClassifier 참조 데이터
    """
    UNKNOWN = "unclassified"

    if syllabus_list is None:
        syllabus_list = []

    print("rule-based 시작\n")


    # Rule 기반
    rule_classifier = RuleBasedClassifier(syllabus_list)
    for file_data in file_data_list:
        if file_data['label'] == UNKNOWN:
            file_data['label'] = rule_classifier.classify(file_data)

    print("ml 시작\n")


    # ML 기반
    ml_classifier = MLClassifier(syllabus_list)
    for file_data in file_data_list:
        if file_data['label'] == UNKNOWN:
            file_data["label"] = ml_classifier.classify(file_data)

    # 결과 반환: 실제 존재하는 키만
    results = [
        {
            "file_name": f.get("file_name"),
            "ml_content": f.get("ml_content"),
            "rule_based_content": f.get("rule_based_content"),
            "label": f.get("label")
        }
        for f in file_data_list
    ]

    return results
