"""Issue similarity detection using TF-IDF + structured boosts."""

from __future__ import annotations

from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from models.schemas import SimilarIssue
from repositories.issue_repository import IssueRepository


class SimilarityService:
    """Service for ranking similar historical issues."""

    def __init__(self) -> None:
        self.issue_repo = IssueRepository()

    @staticmethod
    def _text_blob(title: str | None, description: str | None) -> str:
        return f"{title or ''} {description or ''}".strip()

    def find_similar_issues(
        self,
        title: str,
        description: str,
        module_name: str,
        category_name: str | None,
        error_code: str | None,
        top_n: int = 5,
    ) -> list[SimilarIssue]:
        """Return top similar issues ranked by combined score."""
        candidates = self.issue_repo.list_similarity_candidates()
        if not candidates:
            return []

        input_text = self._text_blob(title, description)
        candidate_texts = [self._text_blob(item.get("title"), item.get("description")) for item in candidates]

        # TF-IDF can fail when all documents are empty or stopwords.
        try:
            vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
            matrix = vectorizer.fit_transform([input_text, *candidate_texts])
            text_scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
        except ValueError:
            text_scores = [0.0 for _ in candidates]

        scored: list[SimilarIssue] = []
        normalized_error_code = (error_code or "").strip().lower()
        normalized_module = module_name.strip().lower()
        normalized_category = (category_name or "").strip().lower()

        for idx, issue in enumerate(candidates):
            text_score = float(text_scores[idx]) if idx < len(text_scores) else 0.0
            boosts: dict[str, float] = {
                "tfidf": round(text_score, 4),
                "error_code_boost": 0.0,
                "module_boost": 0.0,
                "category_boost": 0.0,
                "helpful_resolution_boost": 0.0,
            }

            candidate_error_code = str(issue.get("error_code") or "").strip().lower()
            if normalized_error_code and candidate_error_code and normalized_error_code == candidate_error_code:
                boosts["error_code_boost"] = 0.35

            candidate_module = str(issue.get("module_name") or "").strip().lower()
            if normalized_module and normalized_module == candidate_module:
                boosts["module_boost"] = 0.15

            candidate_category = str(issue.get("category_name") or "").strip().lower()
            if normalized_category and normalized_category == candidate_category:
                boosts["category_boost"] = 0.15

            status = str(issue.get("status") or "")
            avg_rating = float(issue.get("avg_rating") or 0.0)
            helpful_ratio = float(issue.get("helpful_ratio") or 0.0)
            if status in {"Resolved", "Closed"} and avg_rating >= 4.0 and helpful_ratio >= 0.5:
                boosts["helpful_resolution_boost"] = 0.10

            final_score = min(1.0, boosts["tfidf"] + boosts["error_code_boost"] + boosts["module_boost"] + boosts["category_boost"] + boosts["helpful_resolution_boost"])

            scored.append(
                SimilarIssue(
                    issue_id=int(issue["issue_id"]),
                    title=str(issue["title"]),
                    status=status,
                    error_code=str(issue.get("error_code")) if issue.get("error_code") else None,
                    module_name=str(issue.get("module_name") or ""),
                    category_name=str(issue.get("category_name") or ""),
                    score=round(final_score, 4),
                    score_breakdown=boosts,
                )
            )

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_n]
