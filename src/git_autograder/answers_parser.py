import os
from io import TextIOWrapper
from dataclasses import dataclass
from typing import List, Tuple

from git_autograder.exception import GitAutograderInvalidStateException


@dataclass
class GitAutograderAnswersRecord:
    question: str
    answer: str

    def as_tuple(self) -> Tuple[str, str]:
        return self.question, self.answer

    @staticmethod
    def from_tuple(tuple_value: Tuple[str, str]) -> "GitAutograderAnswersRecord":
        return GitAutograderAnswersRecord(
            question=tuple_value[0], answer=tuple_value[1]
        )


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


class GitAutograderAnswersParser:
    def __init__(self, path: str = "../answers.txt") -> None:
        if not os.path.isfile(path):
            raise GitAutograderInvalidStateException(
                "Missing answers.txt file from repository.",
                exercise_name=None,
                is_local=None,
                started_at=None,
            )

        with open(path, "r") as file:
            self.answers: GitAutograderAnswers = self.__parse(file)

    def __parse(self, file: TextIOWrapper) -> GitAutograderAnswers:
        questions: List[str] = []
        answers: List[str] = []
        acc_lines: List[str] = []
        flag = 0  # 0 -> looking for question, 1 -> looking for answer
        for line in file.readlines():
            line = line.strip()
            if line.lower().startswith("q:") or line.lower().startswith("a:"):
                if flag == 0:
                    # If we were waiting for a question and found it, the previous would have been an answer
                    if len(acc_lines) != 0:
                        answers.append(self.__preserve_whitespace_join(acc_lines))
                else:
                    # If we were waiting for an answer and found it, the previous would have been a question
                    if len(acc_lines) != 0:
                        questions.append(self.__preserve_whitespace_join(acc_lines))
                acc_lines = [line[2:].strip()]
                # Once a question/answer is found, we switch the flag around to wait for the next thing
                flag = 1 - flag
            else:
                acc_lines.append(line)

        if len(acc_lines) != 0:
            if flag == 0:
                answers.append(self.__preserve_whitespace_join(acc_lines))
            else:
                questions.append(self.__preserve_whitespace_join(acc_lines))

        if len(questions) != len(answers):
            raise GitAutograderInvalidStateException(
                "Invalid answers format: missing question(s) or answer(s) or both",
                exercise_name=None,
                is_local=None,
                started_at=None,
            )

        return GitAutograderAnswers(questions=questions, answers=answers)

    def __preserve_whitespace_join(
        self, lines: List[str], delimiter: str = "\n"
    ) -> str:
        res = []
        blank_count = 0
        for line in lines:
            if line == "":
                blank_count += 1
                if blank_count > 1:
                    res.append(line)
            else:
                blank_count = 0
                res.append(line)
        return delimiter.join(res).strip()
