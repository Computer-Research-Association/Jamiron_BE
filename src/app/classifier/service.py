from typing import List, Dict
from .methods.rule import RuleBasedClassifier
from .methods.ml import MLClassifier

class ClassifierManager:
    def __init__(self, rule_classifier: RuleBasedClassifier, ml_classifier: MLClassifier):
        self.rule_classifier = rule_classifier
        self.ml_classifier = ml_classifier

    def run_pipeline(self, file_data_list: List[Dict[str, str]]) -> List[Dict[str, str]]:

        # 1. Rule 기반 분류
        for file_data in file_data_list:
            if file_data['label'] == 'unclassified':
                file_data['label'] = self.rule_classifier.classify(file_data)

        rule_based_classified = []

        for file_data in file_data_list:
            print(file_data['label'])
            # if file_data['label'] != 'unclassified':
            #     rule_based_classified.append({'file_name': file_data['file_name'], 'label': file_data['label']})

        print(f"rule-based classify successfully\n {rule_based_classified}")

        # 2. ML 기반 분류 (남은 unclassified만 대상)
        for file_data in file_data_list:
            if file_data['label'] == 'unclassified':
                file_data['label'] = self.ml_classifier.classify(file_data)

        return file_data_list
    
    