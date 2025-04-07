from dataclasses import dataclass
from typing import List, Optional

from git_autograder.answers.answers_record import GitAutograderAnswersRecord


@dataclass
class GitAutograderAnswers:
    questions: List[str]
    answers: List[str]

    @property
    def qna(self) -> List[GitAutograderAnswersRecord]:
        return list(
            map(
                lambda a: GitAutograderAnswersRecord.from_tuple(a),
                zip(self.questions, self.answers),
            )
        )

    def __getitem__(self, key: int) -> GitAutograderAnswersRecord:
        question = self.questions[key]
        answer = self.answers[key]
        return GitAutograderAnswersRecord.from_tuple((question, answer))

    def __len__(self) -> int:
        return len(self.questions)

    def get_by_question(self, question: str) -> Optional[GitAutograderAnswersRecord]:
        for i, q in enumerate(self.questions):
            if question == q:
                return GitAutograderAnswersRecord.from_tuple((q, self.answers[i]))
        return None
