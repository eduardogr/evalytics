from typing import Iterable

from anytree import NodeMixin, PreOrderIter, RenderTree


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
        return PreOrderIter(self.root)

    def __str__(self):
        return '\n'.join(["{0}{1}".format(pre, node) for pre, _, node in RenderTree(self.root)])
