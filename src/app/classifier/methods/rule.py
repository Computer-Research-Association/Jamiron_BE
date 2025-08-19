from typing import List, Dict
from collections import Counter


class RuleBasedClassifier:
    def __init__(self, syllabus: List[Dict]):
        # __init__ 메서드는 syllabus 데이터를 받아 저장합니다.
        self.syllabus = syllabus

    def classify(self, file_data: Dict[str, str]) -> str:
        # file_data 딕셔너리에서 'content' 키를 사용합니다.
        # 이 키가 없으면 오류를 피하기 위해 바로 'unclassified'를 반환합니다.
        file_content = file_data.get('content', '')

        # 강의 계획서 데이터를 순회하며 키워드를 검색합니다.
        for entry in self.syllabus:
            # 강의명이나 강의 코드가 문서 내용에 포함되어 있는지 확인합니다.
            if entry["class_name"] in file_content or entry["class_code"] in file_content:
                # 규칙이 일치하면 해당 강의명으로 분류합니다.
                return entry["class_name"]

        # 어떤 규칙에도 해당하지 않으면 'unclassified'를 반환합니다.
        return 'unclassified'