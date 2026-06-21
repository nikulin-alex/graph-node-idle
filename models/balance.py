"""
Модель баланса игрока.
"""


class Balance:
    """
    Attributes:
        balance: Текущий баланс.
        income: Доход в секунду.
    """

    def __init__(self, initial_balance: int = 0):
        self._balance: int = initial_balance
        self._income: int = 0

    @property
    def balance(self) -> int:
        """Текущий баланс игрока."""
        return self._balance

    @balance.setter
    def balance(self, value: int) -> None:
        """Устанавливает баланс, не позволяя уйти в отрицательные значения."""
        self._balance = max(value, 0)

    @property
    def income(self) -> int:
        """Доход в секунду."""
        return self._income

    def update(self, nodes: list, traversers: list) -> None:
        """
        Обновляет доход и баланс на текущие в соответствии с состоянием системы.

        Args:
            nodes: Список узлов графа (GraphNode)
            traversers: Список обходчиков (Traverser)
        """
        nodes_income = sum(node.level**2 for node in nodes)
        traversers_income = sum(t.get_income() for t in traversers)
        self._income = nodes_income + traversers_income
        self._balance += self.income
