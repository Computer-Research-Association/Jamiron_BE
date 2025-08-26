from typing import List, Dict
from .methods.rule import RuleBasedClassifier
from .methods.ml import MLClassifier

from ..user.router import read_user_syllabuses  # FastAPI router에서 가져오기
from sqlalchemy.orm import Session
from ..config.database import get_db

# ClassifierManager 클래스는 기존과 동일합니다.
class ClassifierManager:
    def __init__(self, rule_classifier: RuleBasedClassifier, ml_classifier: MLClassifier):
        self.rule_classifier = rule_classifier
        self.ml_classifier = ml_classifier

    def run_pipeline(self, file_data_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
        # 1. Rule 기반 분류
        for file_data in file_data_list:
            if file_data['label'] == 'unclassified':
                file_data['label'] = self.rule_classifier.classify(file_data)

        # 2. ML 기반 분류 (남은 unclassified만 대상)
        for file_data in file_data_list:
            if file_data['label'] == 'unclassified':
                file_data['label'] = self.ml_classifier.classify(file_data)

        return file_data_list

def classify_with_ml(user_id: str, year: str, semester: str, db: Session) -> List[Dict[str, str]]:
    # 1. FastAPI router 함수에서 syllabuses 가져오기
    syllabus_data_list: List[Dict[str, str]] = read_user_syllabuses(
        user_id=user_id,
        year=year,
        semester=semester,
        db=db
    )
    rule_classifier = RuleBasedClassifier(syllabus_data_list)
    ml_classifier = MLClassifier(syllabus_data_list)

    manager = ClassifierManager(rule_classifier, ml_classifier)

    return manager.run_pipeline(file_data_list)