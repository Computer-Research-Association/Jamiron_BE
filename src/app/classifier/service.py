from typing import List, Dict
from .models.rule import RuleBasedClassifier
from .models.ml import MLClassifier

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

syllabus_data_list = [
]

def classify_with_ml(file_data_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
    rule_classifier = RuleBasedClassifier(syllabus_data_list)
    ml_classifier = MLClassifier(syllabus_data_list)

    manager = ClassifierManager(rule_classifier, ml_classifier)

    return manager.run_pipeline(file_data_list)