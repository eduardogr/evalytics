from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from anytree import NodeMixin, PreOrderIter, RenderTree


@dataclass
class Employee(NodeMixin):
    """Tree-Node functionallity
    Base model for building the OrgChart

    examples;
        <jhon: 1 minion>
        <jane (business development): 3 minions>
    """

    def __init__(self, mail: str, area: str = None, supervisor=None, minions=None):
        assert '@' in mail
        super().__init__()
        self.mail = mail
        self.area = area
        self.parent = supervisor
        if minions:
            self.children = minions

    @property
    def name(self) -> str:
        return self.mail.split('@')[0]

    @property
    def minions(self) -> Iterable['Employee']:
        return self.children

    def __str__(self):
        minions_count = len(self.children)
        if self.area:
            return '<{0.name} ({0.area}): {1} minions>'.format(self, minions_count)
        return '<{0.name}: {1} minions>'.format(self, minions_count)


class OrgChart:
    """
    example;

    <jane: 1 minions>
     └── <jhon: 3 minions>
         ├── <minion: 0 minions>
         ├── <minion: 0 minions>
         └── <minion: 0 minions>
    """

    def __init__(self, root: Employee):
        assert root is not None
        self.root = root

    def __iter__(self):
        return iter(PreOrderIter(self.root))

    def __str__(self):
        return '\n'.join(["{0}{1}".format(pre, node) for pre, _, node in RenderTree(self.root)])

    def create_eval_suite(self) -> 'EvalSuite':
        evals = []
        for employee in self:
            evals.append(Eval.new_self_eval(employee))

            supervisor = employee.parent
            if supervisor:
                evals.append(
                    Eval.new_supervisor_eval(employee, supervisor)
                )
                for peer in supervisor.minions:
                    if peer is not employee:
                        evals.append(Eval.new_peer_eval(employee, peer))

            for minion in employee.minions:
                evals.append(Eval.new_minion_eval(employee, minion))

        return EvalSuite(evals)


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

    def __init__(self, from_: Employee, to_: Employee, type_: EvalType):
        self.from_ = from_
        self.to_ = to_
        self.type_ = type_

    def __repr__(self):
        return '<Eval: {0.from_.name} --> {0.to_.name} ({0.type_.name})>'\
            .format(self)

    @classmethod
    def new_self_eval(cls, who: Employee) -> 'Eval':
        return cls(who, who, EvalType.SELF)

    @classmethod
    def new_peer_eval(cls, who: Employee, peer: Employee) -> 'Eval':
        return cls(who, peer, EvalType.PEER)

    @classmethod
    def new_supervisor_eval(cls, who: Employee, supervisor: Employee) -> 'Eval':
        return cls(who, supervisor, EvalType.MY_SUPERVISOR)

    @classmethod
    def new_minion_eval(cls, who: Employee, minion: Employee) -> 'Eval':
        return cls(who, minion, EvalType.MY_MINION)


class EvalSuite:

    def __init__(self, initial_evals: Iterable[Eval]):
        self.initial_evals = initial_evals
