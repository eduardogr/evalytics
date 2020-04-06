from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from anytree import NodeMixin, PreOrderIter, RenderTree


@dataclass
class Setup:
    pass


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
class GoogleSetup(Setup):

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
class EmployeeNode(NodeMixin):
    """Tree-Node functionallity
    Base model for building the OrgChart

    examples;
        <jhon: 1 minion>
        <jane (business development): 3 minions>
    """

    def __init__(self, employee: Employee,
                 supervisor: Employee = None, minions=None):
        super().__init__()
        self.employee = employee
        self.parent = supervisor
        if minions:
            self.children = minions

    @property
    def minions(self) -> Iterable['EmployeeNode']:
        return self.children

    def __str__(self):
        minions_count = len(self.children)
        if self.employee.get_team():
            return '<{0.employee.get_uid()} ({0.employee.get_team()}): {1} minions>'.format(
                self, minions_count)
        return '<{0.employee.get_uid()}: {1} minions>'.format(self, minions_count)


class OrgChart:
    """
    example;

    <jane: 1 minions>
     └── <jhon: 3 minions>
         ├── <minion: 0 minions>
         ├── <minion: 0 minions>
         └── <minion: 0 minions>
    """

    def __init__(self, root: EmployeeNode):
        assert root is not None
        self.root = root

    def __iter__(self):
        return iter(PreOrderIter(self.root))

    def __str__(self):
        return '\n'.join(["{0}{1}".format(pre, node)
                          for pre, _, node in RenderTree(self.root)])


class EvalType(Enum):
    SELF = 1
    PEER = 2
    MY_SUPERVISOR = 3
    MY_MINION = 4


@dataclass
class EvalNode:
    """
    examples;

        <Eval: jhon --> Jane (MY_SUPERVISOR)>
        <Eval: minion3 --> minion3 (SELF)>
    """

    def __init__(self, from_: EmployeeNode, to_: EmployeeNode, type_: EvalType):
        self.from_ = from_
        self.to_ = to_
        self.type_ = type_

    def __str__(self):
        return '<EvalNode: {0.from_.name} --> {0.to_.name} ({0.type_.name})>'\
            .format(self)

    @classmethod
    def new_self_eval(cls, who: EmployeeNode) -> 'Eval':
        return cls(who, who, EvalType.SELF)

    @classmethod
    def new_peer_eval(cls, who: EmployeeNode, peer: EmployeeNode) -> 'Eval':
        return cls(who, peer, EvalType.PEER)

    @classmethod
    def new_supervisor_eval(
            cls, who: EmployeeNode, supervisor: EmployeeNode) -> 'Eval':
        return cls(who, supervisor, EvalType.MY_SUPERVISOR)

    @classmethod
    def new_minion_eval(cls, who: EmployeeNode, minion: EmployeeNode) -> 'Eval':
        return cls(who, minion, EvalType.MY_MINION)


@dataclass
class EvalNodeSuite:

    def __init__(self):
        self.evals = []

    def add_eval(self, eval_: Eval):
        self.evals.append(eval_)
