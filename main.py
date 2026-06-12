"""Бюджетный помощник для учета расходов за месяц."""

class ExpenseTreeNode:
    """Узел бинарного дерева расходов."""

    def __init__(self, day, expense):
        """Создает узел с днем и первым расходом."""
        self.day = day
        self.expenses = [expense]
        self.left = None
        self.right = None

class ExpenseTree:
    """Бинарное дерево поиска для хранения расходов по дням."""

    def __init__(self):
        """Создает пустое дерево расходов."""
        self.root = None

    def insert(self, expense):
        """
        Добавляет расход в дерево.
        Вход: expense - словарь с расходом.
        """
        day = expense["day"]

        if self.root is None:
            self.root = ExpenseTreeNode(day, expense)
            return

        current = self.root
        while current is not None:
            if day == current.day:
                current.expenses.append(expense)
                return

            if day < current.day:
                if current.left is None:
                    current.left = ExpenseTreeNode(day, expense)
                    return
                current = current.left
            else:
                if current.right is None:
                    current.right = ExpenseTreeNode(day, expense)
                    return
                current = current.right

    def print_tree(self):
        """Выводит все расходы дерева по возрастанию дней."""
        self._print_node(self.root)

    def _print_node(self, node):
        """Рекурсивно выполняет симметричный обход дерева."""
        if node is None:
            return

        self._print_node(node.left)
        print(f"День {node.day}:")
        for expense in node.expenses:
            amount = expense["amount"]
            category = expense["category"]
            print(f"  Сумма: {amount:.2f} руб. | Категория: {category}")
        self._print_node(node.right)

    def clear(self):
        """Очищает дерево."""
        self.root = None

    def rebuild(self, expenses):
        """
        Перестраивает дерево заново.
        Вход: expenses - список всех расходов.
        """
        self.clear()
        for expense in expenses:
            self.insert(expense)

class BudgetHelper:
    """Основной класс бюджетного помощника."""

    def __init__(self):
        """Создает пустой учет расходов за месяц."""
        self.daily_expenses = [0] * 32
        self.prefix_sums = [0] * 32
        self.expenses = []
        self.undo_stack = []
        self.tree = ExpenseTree()

    def add_expense(self, day, amount, category):
        """
        Добавляет новый расход.
        Вход: day - день, amount - сумма, category - категория.
        Выход: True, если расход добавлен, иначе False.
        """
        if day < 1 or day > 31:
            print("Ошибка: день должен быть числом от 1 до 31.")
            return False

        if amount <= 0:
            print("Ошибка: сумма должна быть положительным числом.")
            return False

        category = category.strip()
        if category == "":
            print("Ошибка: категория не может быть пустой.")
            return False

        expense = {
            "day": day,
            "amount": amount,
            "category": category,
        }

        self.expenses.append(expense)
        self.daily_expenses[day] += amount
        self.undo_stack.append(expense)
        self.tree.insert(expense)
        self.update_prefix_sums()

        print("Расход успешно добавлен.")
        return True

    def update_prefix_sums(self):
        """Пересчитывает массив префиксных сумм за месяц."""
        self.prefix_sums[0] = 0
        for day in range(1, 32):
            self.prefix_sums[day] = (
                self.prefix_sums[day - 1] + self.daily_expenses[day]
            )

    def get_period_sum(self, start_day, end_day):
        """
        Возвращает сумму расходов за период.
        Вход: start_day и end_day - границы периода.
        Выход: сумма расходов или None при ошибке.
        """
        if start_day < 1 or start_day > 31:
            print("Ошибка: день должен быть числом от 1 до 31.")
            return None

        if end_day < 1 or end_day > 31:
            print("Ошибка: день должен быть числом от 1 до 31.")
            return None

        if start_day > end_day:
            print("Ошибка: начальный день не должен быть больше конечного.")
            return None

        # Формула работает за O(1), так как prefix_sums уже построен.
        return self.prefix_sums[end_day] - self.prefix_sums[start_day - 1]

    def find_max_expense_day(self):
        """
        Ищет день с максимальными расходами.
        Используется обычный линейный поиск по дням.
        """
        max_day = 1
        max_sum = self.daily_expenses[1]

        for day in range(2, 32):
            if self.daily_expenses[day] > max_sum:
                max_sum = self.daily_expenses[day]
                max_day = day

        if max_sum == 0:
            print("Расходов пока нет.")
            return None, 0

        return max_day, max_sum

    def get_category_totals(self):
        """
        Считает суммы расходов по категориям.
        Выход: список пар (категория, сумма).
        """
        category_totals = {}

        for expense in self.expenses:
            category = expense["category"]
            amount = expense["amount"]

            if category not in category_totals:
                category_totals[category] = 0

            category_totals[category] += amount

        category_items = []
        for category in category_totals:
            category_items.append((category, category_totals[category]))

        return category_items

    def insertion_sort_categories(self, category_items):
        """
        Сортирует категории по сумме трат.
        Используется сортировка вставками по убыванию суммы.
        """
        for i in range(1, len(category_items)):
            current_item = category_items[i]
            j = i - 1

            while j >= 0 and category_items[j][1] < current_item[1]:
                category_items[j + 1] = category_items[j]
                j -= 1

            category_items[j + 1] = current_item

        return category_items

    def show_categories_by_total(self):
        """Выводит категории по убыванию суммы расходов."""
        category_items = self.get_category_totals()

        if len(category_items) == 0:
            print("Расходов пока нет.")
            return

        sorted_categories = self.insertion_sort_categories(category_items)

        print("Категории по сумме трат:")
        for category, total in sorted_categories:
            print(f"{category}: {total:.2f} руб.")

    def undo_last_expense(self):
        """
        Отменяет последний добавленный расход.
        Последний расход берется из стека undo_stack.
        """
        if len(self.undo_stack) == 0:
            print("Отменять нечего.")
            return

        last_expense = self.undo_stack.pop()
        day = last_expense["day"]
        amount = last_expense["amount"]
        category = last_expense["category"]

        self.daily_expenses[day] -= amount

        for i in range(len(self.expenses) - 1, -1, -1):
            expense = self.expenses[i]
            same_day = expense["day"] == day
            same_amount = expense["amount"] == amount
            same_category = expense["category"] == category

            if same_day and same_amount and same_category:
                del self.expenses[i]
                break

        self.update_prefix_sums()
        self.rebuild_tree()

        print(
            "Последний расход отменён: "
            f"день {day}, сумма {amount:.2f} руб., категория: {category}."
        )

    def show_all_expenses(self):
        """Выводит список всех расходов."""
        if len(self.expenses) == 0:
            print("Расходов пока нет.")
            return

        print("Все расходы:")
        for expense in self.expenses:
            day = expense["day"]
            amount = expense["amount"]
            category = expense["category"]
            print(
                f"День: {day} | "
                f"Сумма: {amount:.2f} руб. | "
                f"Категория: {category}"
            )

    def show_tree(self):
        """Выводит дерево расходов."""
        if self.tree.root is None:
            print("Дерево расходов пустое.")
            return

        print("Расходы в дереве по дням:")
        self.tree.print_tree()

    def rebuild_tree(self):
        """Перестраивает дерево расходов."""
        self.tree.rebuild(self.expenses)

def add_demo_data(helper):
    """Добавляет демонстрационные расходы для проверки."""
    demo_expenses = [
        (1, 500, "еда"),
        (2, 120, "транспорт"),
        (5, 1500, "одежда"),
        (5, 700, "еда"),
        (10, 3000, "техника"),
        (15, 900, "кафе"),
        (20, 200, "транспорт"),
        (25, 2500, "подарки"),
    ]

    print("Добавление демонстрационных данных:")
    for day, amount, category in demo_expenses:
        helper.add_expense(day, amount, category)

def read_day(message):
    """Считывает день месяца и проверяет его."""
    try:
        day = int(input(message))
    except ValueError:
        print("Ошибка: день должен быть числом от 1 до 31.")
        return None

    if day < 1 or day > 31:
        print("Ошибка: день должен быть числом от 1 до 31.")
        return None
    return day

def read_amount(message):
    """Считывает сумму расхода и проверяет ее."""
    try:
        amount = float(input(message))
    except ValueError:
        print("Ошибка: сумма должна быть положительным числом.")
        return None

    if amount <= 0:
        print("Ошибка: сумма должна быть положительным числом.")
        return None

    return amount

def handle_add_expense(helper):
    """Обрабатывает добавление расхода через меню."""
    day = read_day("Введите день месяца (1-31): ")
    if day is None:
        return

    amount = read_amount("Введите сумму расхода: ")
    if amount is None:
        return

    category = input("Введите категорию: ")
    helper.add_expense(day, amount, category)

def handle_period_sum(helper):
    """Обрабатывает запрос суммы за период."""
    start_day = read_day("Введите начальный день: ")
    if start_day is None:
        return

    end_day = read_day("Введите конечный день: ")
    if end_day is None:
        return

    period_sum = helper.get_period_sum(start_day, end_day)
    if period_sum is not None:
        print(f"Сумма расходов за период: {period_sum:.2f} руб.")

def handle_max_day(helper):
    """Обрабатывает поиск дня с максимальными расходами."""
    day, amount = helper.find_max_expense_day()
    if day is not None:
        print(
            f"День с максимальными расходами: {day}, "
            f"сумма: {amount:.2f} руб."
        )

def print_menu():
    """Выводит главное меню программы."""
    print()
    print("Меню:")
    print("1. Добавить расход")
    print("2. Показать все расходы")
    print("3. Посчитать сумму расходов за период")
    print("4. Найти день с максимальными расходами")
    print("5. Показать категории по сумме трат")
    print("6. Отменить последний добавленный расход")
    print("7. Показать дерево расходов")
    print("8. Выйти")

def main():
    """Запускает консольное меню бюджетного помощника."""
    helper = BudgetHelper()

    load_demo = input("Загрузить демонстрационные данные? 1 — да, 0 — нет: ")
    if load_demo == "1":
        add_demo_data(helper)

    while True:
        print_menu()
        choice = input("Выберите пункт меню: ")

        if choice == "1":
            handle_add_expense(helper)
        elif choice == "2":
            helper.show_all_expenses()
        elif choice == "3":
            handle_period_sum(helper)
        elif choice == "4":
            handle_max_day(helper)
        elif choice == "5":
            helper.show_categories_by_total()
        elif choice == "6":
            helper.undo_last_expense()
        elif choice == "7":
            helper.show_tree()
        elif choice == "8" or choice == "0":
            print("Программа завершена.")
            break
        else:
            print("Ошибка: выберите пункт меню от 1 до 8.")

if __name__ == "__main__":
    main()