from typing import List, Dict
from .methods.rule import RuleBasedClassifier
from .methods.ml import MLClassifier

# 1. 강의 계획서 데이터(syllabus)를 여기에 정의합니다.
# 이 데이터는 규칙 기반 분류기의 '지식' 역할을 합니다.
syllabus_data_list = [
    {
        "class_name": "AI개론",
        "class_code": "ECE30008",
        "professor_name": "",
        "prof_email": "",
        "year": "2025",
        "hakgi": "1",
        "objectives": "Introduce fundamental concepts and practical techniques in artificial intelligence.",
        "description": "This course introduces fundamental concepts, key subfields, and emerging trends in artificial intelligence. Students will explore theoretical foundations and practical applications. Students will also gain hands-on experience with AI techniques using Python. The course aims to build a solid foundation for advanced topics such as machine learning and deep learning.",
        "schedule": "Python programming language 1\nPython programming language 2\nWorking with data 1\nWorking with data 2\nWorking with data 3\nIntelligent agent\nMidterm Exam\nClustering\nRegression\nClassification\nSearch 1\nSearch 2\nGame trees, Adversarial search\nOther types of AI; AI ethics\nFinal exam"
    },
    {
        "class_name": "Database System",
        "class_code": "ITP30010",
        "professor_name": "",
        "prof_email": "",
        "year": "2025",
        "hakgi": "1",
        "objectives": "Study data modeling and database query techniques using DBMS and SQL.",
        "description": "This is an introductory course on Database Management Systems (DBMSs). Students will study DBMS concepts, design data models, and execute SQL queries. They will also explore trends in data storage and data science practices.",
        "schedule": "Admin, Introduction DBMS, Relation data model\nRelational algebra Getting a DBMS\nStructured Query Language (DML)\nStructured Query Language (DDL)\nMore Structured Query Language\nEntity-Rleationship (ER) diagrams\nNormalization theory\nAdvanced SQL, Constraints, Views\nMidterm\nTransactions\nDatabase Storages\nIndexes\nIndexes\nKeys, Functions/Procedures, Triggers\nBeyond relational data\nFinal Exam"
    },
    {
        "class_name": "알고리듬분석",
        "class_code": "ECE30011",
        "professor_name": "",
        "prof_email": "",
        "year": "2025",
        "hakgi": "1",
        "objectives": "Learn and analyze various algorithm design techniques with C programming.",
        "description": "This course teaches various algorithmic techniques and the analysis of algorithms. Students will study design strategies including recursion, dynamic programming, and greedy methods, and implement them in C.",
        "schedule": "Introduction / Analyzing & Designing Algorithms\nAsymptotic Notation / Recursion & Induction\nExercise / Dynamic programming intro\nMCM problem / LCS problem\nGreedy algorithms / Quiz1\nQuiz1 review / Huffman class_code\nKnapsack problem / Graph (BFS/DFS: e-learning)\nMidterm\nMidterm review / Topological sort / Critical path / Biconnected\nMST(e-learning) / Bellman Ford / DAG\nDijkstra / Floyd-Warshall algorithm / Rabin-Karp algorithm\nKMP algorithm / Red-Black tree\nAverage case analysis / Quiz2\nQuiz2 review / Linear time sorting\nOrder statistics / NP-completeness / Approximation algorithm\nFinal"
    },
    {
        "class_name": "운영체제",
        "class_code": "ECE30021",
        "professor_name": "",
        "prof_email": "",
        "year": "2025",
        "hakgi": "1",
        "objectives": "Understand core principles and implementation details of modern operating systems.",
        "description": "Introduction to core concepts and principles in operating systems, with emphasis on process and storage management. Programming assignments in UNIX/Linux using threads, shared memory, and synchronization.",
        "schedule": "Introduction\nOperating System structures\nOperating System structures\nProcess\nProcess\nThreads\nProcess synchronization\nMidtem test\nProcess synchronization\nCPU scheduling\nCPU scheduling\nMain memory\nMain memory\nVirtual memory\nVirtual memory\nFinal test"
    }
]

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
        
        # ... (중략) ...
        
        # 2. ML 기반 분류 (남은 unclassified만 대상)
        for file_data in file_data_list:
            if file_data['label'] == 'unclassified':
                file_data['label'] = self.ml_classifier.classify(file_data)
        
        return file_data_list


def classify_with_ml(file_data_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
    # RuleBasedClassifier와 마찬가지로,
    # MLClassifier 객체 생성 시에도 syllabus_data_list를 인자로 전달해야 합니다.
    rule_classifier = RuleBasedClassifier(syllabus_data_list) 
    ml_classifier = MLClassifier(syllabus_data_list) # 이 부분이 수정되었습니다.

    manager = ClassifierManager(rule_classifier, ml_classifier)
    return manager.run_pipeline(file_data_list)