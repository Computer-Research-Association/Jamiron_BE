from typing import List, Dict
from collections import Counter


class RuleBasedClassifier:
    def __init__(self, syllabus: List[Dict[str, str]]):
        self.syllabus = syllabus

    def count_prof_name(self):
        prof_names = [entry['professor_name'] for entry in self.syllabus]
        prof_count = Counter(prof_names)

        for idx, entry in enumerate(self.syllabus):
            # 각 row에 해당 교수이름의 등장 횟수를 추가
            entry['p_c'] = str(prof_count[entry['professor_name']])

            # 마지막 원소라면 출력
            if idx == len(self.syllabus) - 1:
                print(f"{entry} (마지막 원소!)")
                print(f"{entry['p_c']} (카운트!)")

        return self.syllabus


    def classify(self, file: Dict[str, str]) -> str:
        self.count_prof_name()
        for entry in self.syllabus:
            if entry["class_code"] in file["rule_based_content"]:
                return entry["class_name"]
            elif entry["class_name"] in file["rule_based_content"]:
                return entry["class_name"]
            elif entry['p_c'] == '1' and entry['professor_name'] in file["rule_based_content"]:
                return entry["class_name"]
            else: return "unclassified"