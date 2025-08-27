import os
import numpy as np
import sys
import pandas as pd
from scipy.spatial.distance import cosine
#import json
from sentence_transformers import SentenceTransformer
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Any

def extract_key_sentences_tfidf(text: str, top_k: int = 10) -> List[str]:
    """TF-IDF를 사용해 텍스트에서 주요 문장들을 추출합니다."""
    sentences = sent_tokenize(text)

    if len(sentences) <= top_k:
        return sentences
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences)
    scores = tfidf_matrix.sum(axis=1)

    scored_sentences = [(sentences[i], scores[i, 0]) for i in range(len(sentences))]
    top_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)[:top_k]
    return [s for s, _ in top_sentences]

def get_summary_embedding(text_content: str, model: SentenceTransformer, top_k: int = 10) -> np.ndarray:
    """주요 문장들을 추출한 뒤 평균 임베딩을 계산합니다."""
    if not text_content.strip():
        embedding_dim = model.get_sentence_embedding_dimension()
        return np.zeros(embedding_dim, dtype=np.float32)
    key_sentences = extract_key_sentences_tfidf(text_content, top_k=top_k)
    embeddings = model.encode(key_sentences, convert_to_numpy=True)
    return np.mean(embeddings, axis=0)

def transform_syllabus_to_classifier_format(syllabus_list: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    transformed_data = []
    for syllabus in syllabus_list:
        # label을 class_name 또는 class_code 기반으로 설정
        label = syllabus.get("syllabus_class_name") or "unknown_course"
        content_parts = [
            syllabus.get("syllabus_class_name", ""),
            syllabus.get("syllabus_class_code", ""),
            syllabus.get("syllabus_professor_name", ""),
            syllabus.get("syllabus_objectives", ""),
            syllabus.get("syllabus_description", ""),
            syllabus.get("syllabus_schedule", "")
        ]
        content = " ".join([part for part in content_parts if part])
        if content:
            transformed_data.append({
                "label": label,    # 여기서 label이 강의 이름으로 들어가야 함
                "content": content
            })
    return transformed_data


# --- 2. ML 기반 분류기 클래스 (핵심 로직) ---
def _load_sentence_bert_model(model_name: str) -> SentenceTransformer:
    """Sentence-BERT 모델을 로드합니다."""
    print(f"\n{'='*50}\n 🧠 Sentence-BERT 모델 로드 중: {model_name}\n{'='*50}")
    try:
        model = SentenceTransformer(model_name)
        print(f"✅ {model_name} 모델 로드 완료.")
        return model
    except Exception as e:
        print(f"[오류] Sentence-BERT 모델 로드 실패: {e}", file=sys.stderr)
        sys.exit(1)


class MLClassifier:
    """Sentence-BERT 모델과 코사인 유사도를 기반으로 텍스트를 분류합니다."""

    def __init__(self, syllabus: List[Dict[str, str]], model_name: str = 'sentence-transformers/all-mpnet-base-v2'):
        self.model = _load_sentence_bert_model(model_name)
        self.reference_data = transform_syllabus_to_classifier_format(syllabus)
        self.reference_data = self._embed_reference_data(self.reference_data)
        if not self.reference_data:
            print("[경고] 참조 데이터를 로드하거나 임베딩하는 데 실패했습니다.", file=sys.stderr)

    def _embed_reference_data(self, reference_data: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """참조 데이터에 대한 임베딩을 생성합니다."""
        print(f"\n📚 {len(reference_data)}개의 참조 파일 벡터화 시작...")
        embedded_data = []
        for item in reference_data:
            text = item.get("content", "")
            label = item.get("label", "unknown")
            if text:
                embedding = get_summary_embedding(text, self.model)
                embedded_data.append({
                    "label": label,
                    "embedding": embedding
                })
        print(f"✅ {len(embedded_data)}개의 참조 파일 벡터화 완료.")
        return embedded_data

    def classify_single(self, file_data: str) -> Dict[str, str]:
        
        if not self.reference_data:
            return {"label": "분류불가 (참조데이터 없음)", "details": {}}
        if not file_data:
            return {"label": "미분류 (콘텐츠 없음)", "details": {}}
        query_vec = get_summary_embedding(file_data, self.model)
        if query_vec.size == 0:
            return {"label": "미분류 (임베딩 실패)", "details": {}}
        similarities = []
        for ref in self.reference_data:
            if ref["embedding"].size == 0:
                continue
            similarity = 1 - cosine(query_vec, ref["embedding"])

            similarities.append({
                "label": ref["label"],
                "similarity": similarity
            })


        if not similarities:
            return {"label": "미분류 (유사도 계산 불가)", "details": {}}
        
        sorted_similarities = sorted(similarities, key=lambda x: x["similarity"], reverse=True)
        top_1_match = sorted_similarities[0]
        top_1_label = top_1_match["label"]
        top_1_similarity = top_1_match["similarity"]

        SIMILARITY_THRESHOLD = 0.30
        DIFFERENCE_THRESHOLD = 0.02

        assigned_label = "미분류"
        details = {item['label']: item['similarity'] for item in sorted_similarities}

        if top_1_similarity >= SIMILARITY_THRESHOLD:
            if len(sorted_similarities) > 1:
                top_2_similarity = sorted_similarities[1]["similarity"]
                if (top_1_similarity - top_2_similarity) >= DIFFERENCE_THRESHOLD:
                    assigned_label = top_1_label
                else:
                    assigned_label = "미분류 (유사도 차이 미달)"
            else:
                assigned_label = top_1_label
        else:
            assigned_label = "미분류 (유사도 임계치 미달)"
        return {"label": assigned_label, "details": details}

    def classify(self, file_data: Dict[str, str]) -> str:
        """
        단일 파일 데이터를 입력받아 ML 기반으로 분류를 수행하고
        분류된 레이블(문자열)을 반환합니다.
        """
        if not file_data:
            print("❗ 분류할 파일 데이터가 없어 작업을 종료합니다.")
            return "미분류 (콘텐츠 없음)"
        
        content = file_data.get("rule_based_content", "")
        
        classification_result = self.classify_single(content)
        print(f" 분류완료!! 강의이름: {file_data.get('file_name')}, {classification_result['label']}")
        
        return classification_result['label']