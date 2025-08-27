from typing import List, Dict
from src.app.classifier.methods.rule import RuleBasedClassifier
from src.app.classifier.methods.ml import MLClassifier

def classify_with_rule_and_ml(file_data_list: List[Dict], db=None) -> List[Dict]:
    """
    1. Rule 기반 분류 → label이 unclassified인 경우만
    2. ML 기반 분류 → 남은 unclassified만
    """
    UNKNOWN = "unclassified"

    # Rule 기반
    rule_classifier = RuleBasedClassifier(file_data_list)
    for file_data in file_data_list:
        if file_data.get("label") == UNKNOWN:
            file_data["label"] = rule_classifier.classify(file_data)

    # ML 기반
    ml_classifier = MLClassifier(file_data_list)
    for file_data in file_data_list:
        if file_data.get("label") == UNKNOWN:
            file_data["label"] = ml_classifier.classify(file_data)

    return file_data_list
