from dataclasses import dataclass
from enum import Enum
from typing import Iterable
from json import JSONEncoder

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


@dataclass
class Eval180:

    def __init__(self, self_eval: str, manager_eval: str):
        self.self_eval = self_eval
        self.manager_eval = manager_eval
    
    def to_json(self):
        return {
            'self_eval': self.self_eval,
            'manager_eval': self.manager_eval
        }


@dataclass
class Employee:

    def __init__(self, mail: str, manager: str, eval_180: Eval180):
        assert '@' in mail
        self.mail = mail
        self.manager = manager
        self.eval_180 = eval_180

    @property
    def uid(self) -> str:
        return self.mail.split('@')[0]

    def to_json(self):
        return {
            'mail': self.mail,
            'uid': self.uid,
            'manager': self.manager,
            'eval': self.eval_180.to_json()
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
class Eval:
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
        return '<Eval: {0.from_.name} --> {0.to_.name} ({0.type_.name})>'\
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
class EvalSuite:

    def __init__(self):
        self.evals = []

    def add_eval(self, eval_: Eval):
        self.evals.append(eval_)
