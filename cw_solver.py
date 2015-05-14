#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#= Imports ====================================================================
from db_api import get_answers


#= Objects ====================================================================
class Croft:
    VALUES = {
        "NONE": ". ",
        "EMPTY": "  ",
        "A": "A ",
        "B": "B ",
        "C": "C ",
        "D": "D ",
        "E": "E ",
        "F": "F ",
        "G": "G ",
        "H": "H ",
        "CH": "CH",
        "I": "I ",
        "J": "J ",
        "K": "K ",
        "L": "L ",
        "M": "M ",
        "N": "N ",
        "O": "O ",
        "P": "P ",
        "Q": "Q ",
        "R": "R ",
        "S": "S ",
        "T": "T ",
        "U": "U ",
        "V": "V ",
        "W": "W ",
        "Y": "Y ",
        "Z": "Z ",
        "AL": "Á ",
        "CD": "Č ",
        "DD": "Ď ",
        "EL": "É ",
        "ED": "Ě ",
        "IL": "Í ",
        "ND": "Ň ",
        "OL": "Ó ",
        "RD": "Ř ",
        "SD": "Š ",
        "TD": "Ť ",
        "UL": "Ú ",
        "UR": "Ů ",
        "YL": "Ý ",
        "ZD": "Ž "
    }

    def __init__(self, value=VALUES["NONE"]):
        if value not in self.VALUES.values():
            raise ValueError("`value` must be element of Croft.VALUES")

        self.value = value

    def fit_in(self, croft):
        if not isinstance(croft, Croft):
            raise ValueError("`croft` must be instance of Croft")

        if self.VALUES["NONE"] in (croft.value, self.value):
            return False

        if croft.value in (self.value, self.VALUES["EMPTY"]):
            return True
        else:
            return False

    def __str__(self):
        return self.value

    @classmethod
    def str2crofts(cls, string):
        s = string.upper()

        crofts = list()
        c = False

        for ch in s:
            if c:
                c = False

                if ch == "H":
                    crofts.append(cls(cls.VALUES["CH"]))
                    continue
                else:
                    crofts.append(cls(cls.VALUES["C"]))

            if ch == "C":
                c = True
                continue

            for val in cls.VALUES.values():
                if ch == val[0]:
                    crofts.append(cls(val))
                    break

        return crofts


class Grid:
    """Grid of a crossword"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.grid = [[Croft() for y in range(y)] for x in range(x)]

    def __str__(self):
        string = ""
        for x in self.grid:
            for y in x:
                string += str(y) + " "

            string += "\n"

        return string

    def __getitem__(self, coords):
        return self.grid[coords[0]][coords[1]]

    def __setitem__(self, coords, val):
        if val in Croft.VALUES.values():
            self.grid[coords[0]][coords[1]].value = val
        else:
            raise ValueError("New value must be value from Croft.VALUES")
        

class Question:
    HORIZ = "horizontal"
    VERTIC = "vertical"

    def __init__(self, direction, crofts, hint=None):
        if direction in (self.HORIZ, self.VERTIC):
            self.direction = direction
        else:
            raise ValueError("`direction` must be Question.HORIZ or Question.VERTIC")

        self.crofts = crofts
        self.hint = hint

    def __len__(self):
        return len(self.crofts)

    def is_solved(self):
        return all(c.value is not Croft.VALUES["EMPTY"] for c in self.crofts)
        

class CrossWord:
    def __init__(self, x, y):
        self.grid = Grid(x, y)
        self.questions = list()

    def set_question(self, x, y, direction, length, hint=None):
        if direction is Question.HORIZ:
            x2 = x + 1
            y2 = y + length
        elif direction is Question.VERTIC:
            x2 = x + length
            y2 = y + 1
        else:
            raise ValueError("`direction` must be Question.HORIZ or Question.VERTIC")

        crofts = list()
        for x in range(x, x2):
            for y in range(y, y2):
                self.grid[(x, y)] = Croft.VALUES["EMPTY"]
                crofts.append(self.grid[(x, y)])

        self.questions.append(Question(direction, crofts, hint))

    def get_question_by_croft(self, croft, direction):
        if direction not in (Question.HORIZ, Question.VERTIC):
            raise ValueError("`direction` must be Question.HORIZ or Question.VERTIC")

        if not isinstance(croft, Croft):
            raise ValueError("`croft` must be instance of Croft")

        for question in self.questions:
            if question.direction is not direction:
                continue

            if croft in question.crofts:
                return question


class CrossWordSolver:
    def __init__(self, cw=None):
        if cw is not None:
            self.set_crossword(cw)

    def set_crossword(self, cw):
        if isinstance(cw, CrossWord):
            self.crossword = cw
        else:
            raise ValueError("Argument isn't instance of CrossWord")

    def solve_crossword(self):
        for question in self.crossword.questions:
            self.start_solving(question)

    def start_solving(self, question):
        if not isinstance(question, Question):
            raise ValueError("`question` argument must instance of Question")

        if question.is_solved():
            return True

        if question.direction is Question.HORIZ:
            cross_direction = Question.VERTIC
        else:
            cross_direction = Question.HORIZ

        result = (-1, None)
        answers = get_answers(question.hint, len(question))

        for answer in answers:
            score = 0
            answer = Croft.str2crofts(answer)

            if not self.cohere(question.crofts, answer):
                continue

            for i in range(len(question)):
                crossed = self.crossword.get_question_by_croft(question.crofts[i], cross_direction)

                if isinstance(crossed, Question):
                    index = crossed.crofts.index(question.crofts[i])
                    score += self.test_croft(crossed, index, answer[i])

            if score > result[0]:
                result = (score, answer)

        if result[0] > -1:
            for i in range(len(question)):
                question.crofts[i].value = result[1][i].value

            for c in question.crofts:
                crossed = self.crossword.get_question_by_croft(c, cross_direction)

                if isinstance(crossed, Question):
                    self.start_solving(crossed)

            return True

        else:
            return False

    def test_croft(self, question, index, new):
        answers = get_answers(question.hint, len(question))

        for answer in answers:
            answer = Croft.str2crofts(answer)

            if not self.cohere(question.crofts, answer):
                continue

            if answer[index].value == new.value:
                return 1

        return 0

    @staticmethod
    def cohere(crofts, answer):
        if len(crofts) == len(answer):
            if all(answer[i].fit_in(crofts[i]) for i in range(len(answer))):
                return True

        return False


#= Main program ===============================================================
if __name__ == '__main__':
    cw = CrossWord(5, 10)
    cw.set_question(1, 2, Question.VERTIC, 3, "latinský pozdrav")
    cw.set_question(1, 2, Question.HORIZ, 5, "den mayského kalendáře")
    cw.set_question(3, 2, Question.HORIZ, 6, "záhada zastarale")
    solver = CrossWordSolver(cw)
    solver.solve_crossword()
    print(cw.grid)
