from dataclasses import dataclass
from enum import Enum

@dataclass
class GoogleFile:

    def __init__(self, name, id):
        self.name = name
        self.id = id

    def to_json(self):
        return {
            'name': self.name,
            'id': self.id
        }


@dataclass
class GoogleSetup():

    def __init__(self, folder: GoogleFile, files: [GoogleFile]):
        self.folder = folder
        self.files = files

    def to_json(self):
        return {
            'folder': self.folder.to_json(),
            'files': [f.to_json() for f in self.files]
        }


class EvalKind(Enum):
    SELF = 1
    PEER = 2
    PEER_MANAGER = 3
    MANAGER_PEER = 4

    @staticmethod
    def from_str(label):
        if label == 'SELF':
            return EvalKind.SELF
        elif label == 'PEER':
            return EvalKind.PEER
        elif label == 'PEER_MANAGER':
            return EvalKind.PEER_MANAGER
        elif label == 'MANAGER_PEER':
            return EvalKind.MANAGER_PEER
        else:
            raise NotImplementedError(label)

@dataclass
class Eval:

    def __init__(self, reviewee: str, kind: EvalKind, form: str):
        self.reviewee = reviewee
        self.kind = kind
        self.form = form

    def to_json(self):
        return {
            "reviewee": self.reviewee,
            "kind": self.kind.name,
            "form": self.form
        }

    def __eq__(self, other):
        if type(other) is type(self):
            return self.reviewee == other.reviewee and \
                self.kind == other.kind and \
                self.form == other.form

        return False

    def __hash__(self):
        return hash("%s-%s-%s " %(self.reviewee, self.kind, self.form))


@dataclass
class Employee:

    def __init__(self, mail: str, manager: str, area: str):
        assert '@' in mail
        self.mail = mail
        self.manager = manager
        self.area = area

    @property
    def uid(self) -> str:
        return self.mail.split('@')[0]

    @property
    def has_manager(self) -> bool:
        return bool(self.manager)

    def to_json(self):
        return {
            "mail": self.mail,
            "uid": self.uid,
            "manager": self.manager,
            "area": self.area,
        }

    def __eq__(self, other):
        if type(other) is type(self):
            return self.uid == other.uid
        return False

    def __hash__(self):
        return hash(self.uid)

@dataclass
class Reviewer:

    def __init__(self, employee: Employee, evals={}):
        self.employee = employee
        self.evals = evals

    @property
    def uid(self) -> str:
        return self.employee.uid

    @property
    def mail(self) -> str:
        return self.employee.mail

    def __str__(self):
        return "%s" % self.to_json()

    def to_json(self):
        return {
            "employee": self.employee.to_json(),
            "evals": [e.to_json() for e in self.evals]
        }

@dataclass
class ReviewerResponse:

    def __init__(self,
                 reviewee, reviewer,
                 eval_kind, eval_response,
                 filename, line_number):
        self.reviewee = reviewee
        self.reviewer = reviewer
        self.eval_kind = eval_kind
        self.eval_response = eval_response
        self.filename = filename
        self.line_number = line_number
