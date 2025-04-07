import os

import pytest

from src.git_autograder.answers.answers_parser import GitAutograderAnswersParser
from src.git_autograder.exception import (
    GitAutograderException,
    GitAutograderInvalidStateException,
)


def get_path(filename: str) -> str:
    cur_dir = os.getcwd()
    path = os.path.join(cur_dir, f"tests/data/{filename}.txt")
    return path


def test_missing_answers():
    empty_path = os.getcwd()
    with pytest.raises(
        (GitAutograderInvalidStateException, GitAutograderException, Exception)
    ):
        GitAutograderAnswersParser(path=empty_path)


def test_single_line_answers():
    parser = GitAutograderAnswersParser(path=get_path("single_line_answers"))
    assert len(parser.answers) == 1
    assert parser.answers[0].question == "Hello"
    assert parser.answers[0].answer == "World"


def test_single_line_with_gap_answers():
    parser = GitAutograderAnswersParser(path=get_path("single_line_with_gap_answers"))
    assert len(parser.answers) == 1
    assert parser.answers[0].question == "Hello"
    assert parser.answers[0].answer == "World"


def test_multiple_questions_answers():
    parser = GitAutograderAnswersParser(path=get_path("multiple_questions_answers"))
    assert len(parser.answers) == 2
    assert parser.answers[0].question == "Something"
    assert parser.answers[0].answer == "New"
    assert parser.answers[1].question == "This is"
    assert parser.answers[1].answer == "Quite fun!"


def test_multiline_answers():
    parser = GitAutograderAnswersParser(path=get_path("multiline_answers"))
    assert len(parser.answers) == 2
    assert (
        parser.answers[0].question
        == "This is a question\n\nThat may span multiple lines\n\nThis is a unique problem!"
    )
    assert (
        parser.answers[0].answer
        == "This is also an answer that\n\nWill span more than just a single line\n\n```\nThere is some weird syntax here too!\n```"
    )
    assert parser.answers[1].question == "regular question but with lowercase"
    assert parser.answers[1].answer == "REGULAR ANSWER BUT WITH UPPERCASE"


def test_invalid_answers():
    for i in range(1, 4):
        with pytest.raises(
            (GitAutograderInvalidStateException, GitAutograderException, Exception)
        ):
            GitAutograderAnswersParser(path=get_path(f"invalid_answers_{i}"))


def test_answer_as_list():
    parser = GitAutograderAnswersParser(path=get_path("answers_list"))
    answers = parser.answers[0].answer_as_list()
    assert answers[0] == "Something"
    assert answers[1] == "Else\nIs happening"


def test_get_by_question():
    parser = GitAutograderAnswersParser(path=get_path("single_line_answers"))
    hello_answer = parser.answers.get_by_question("Hello")
    assert parser.answers.get_by_question("Bye") is None
    assert hello_answer is not None
    assert hello_answer.answer == "World"
