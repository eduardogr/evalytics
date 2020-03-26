from anytree import NodeMixin, RenderTree, PreOrderIter


class Employee(NodeMixin):
    """Tree-Node functionallity
    Base model for building the OrgChart

    examples;
        <jhon@tuenti.com: 1>
        <jane@tuenti.com (business development): 3>
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
    def minions(self) -> int:
        return len(self.children)

    def __str__(self):
        if self.area:
            return '<{0.mail} ({0.area}): {0.minions}>'.format(self)
        return '<{0.mail}: {0.minions}>'.format(self)


class OrgChart:
    """
    example;

    <jane@tuenti.com: 1>
     └── <jhon@tuenti.com: 3>
         ├── <minion1@tuenti.com: 0>
         ├── <minion2@tuenti.com: 0>
         └── <minion3@tuenti.com: 0>
    """

    def __init__(self, root: Employee):
        assert root is not None
        self.root = root

    def __iter__(self):
        return PreOrderIter(self.root)

    def __str__(self):
        return '\n'.join(["{0}{1}".format(pre, node) for pre, _, node in RenderTree(self.root)])
