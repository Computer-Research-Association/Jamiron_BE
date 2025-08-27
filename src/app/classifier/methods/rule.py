from typing import List, Dict
from collections import Counter

CONTENT = 'rule_based_content'
CLASS= 'syllabus_class_name'
PROFESSOR = 'syllabus_professor_name'
COUNT = 'professor_count'


class RuleBasedClassifier:

    def __init__(self, syllabus_list: List[Dict[str, str]]):
        self.syllabus_list = syllabus_list
        self.count_prof_name()

    def count_prof_name(self):
        prof_names = [syllabus[PROFESSOR] for syllabus in self.syllabus_list]
        prof_count = Counter(prof_names)

        for idx, syllabus in enumerate(self.syllabus_list):
            if syllabus[PROFESSOR] == "" or syllabus[PROFESSOR] == " ":
                syllabus[COUNT] = "2"
            else:
                syllabus[COUNT] = str(prof_count[syllabus[PROFESSOR]])
        return self.syllabus_list


    def classify(self, file: Dict[str, str]) -> str:
        for syllabus in self.syllabus_list:
            match True:
                case _ if syllabus["class_code"] in file[CONTENT]:
                    return syllabus[CLASS]
                case _ if syllabus[CLASS] in file[CONTENT]:
                    return syllabus[CLASS]
                case _ if syllabus[COUNT] == "1" and syllabus[PROFESSOR] in file[CONTENT]:
                    return syllabus[CLASS]

        return 'unclassified'