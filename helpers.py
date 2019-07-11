from dataclasses import dataclass

from viki.data import TaxSystem, DocumentType, CutFlag, PaymentType, SubjectMatter, CloseDocData, KKTStatus
from viki.kkt import KKT, KKTAccess


class ItemTax:
    """
    Налог на товар
    ВНИМАНИЕ!
    Кофигурация налогов хранится непосредственно в кассе! Но обычно настроено так
    """
    TAX_20 = 1
    TAX_10 = 2
    TAX_0 = 3


@dataclass
class Item:
    title: str
    count: float
    price: float
    tax: ItemTax
    payment: PaymentType
    subject: SubjectMatter


class Cheque:
    """Чек"""

    def __init__(self, document_type: DocumentType):
        self.type = document_type
        self.items: [Item] = []

    @property
    def total(self) -> float:
        """Сумма чека"""
        result = 0.0
        for item in self.items:
            result = result + item.count * item.price
        return result


class ShiftHelper(KKTAccess):

    def open(self):
        """Открыть смену"""
        if not self.status():
            self.kkt.open_shift()

    @property
    def number(self) -> int:
        return self.kkt.register.current_shift

    def status(self) -> bool:
        """
        Статус смены
        :return: открыта или закрыта
        """
        return self.kkt.status.current.shift_open

    def close(self):
        """Закрыть смену"""
        if self.status():
            self.kkt.close_shift()


class KKTHelper:
    """
    Класс реализующий базовые принципы работы с кассой

    Надо добавить больше проверок на состояние кассы
    """

    def __init__(self, port: str,
                 operator_inn: str,
                 operator: str,
                 tax_system: TaxSystem):
        """

        :param port: порт кассы
        :param operator_inn: ИНН оператора
        :param operator: Имя оператора
        :param tax_system: Система налогообложения
        """
        # TODO Брать tax_system из натсроек кассы
        self.kkt = KKT(port, operator_inn, operator, tax_system)
        self.kkt.begin()
        self.check()

    def check(self):
        if not self.kkt.status.fatal.check():
            raise Exception("Фатальная ошибка ККТ!")
        if self.kkt.status.current.no_begin:
            raise Exception("Ошибка начала работы")
        if self.kkt.status.current.shift_more_24:
            raise Exception("Смена открыта более 24 часов!")

    @property
    def shift(self):
        """Управление сменой"""
        return ShiftHelper(self.kkt)

    def print_cheque(self, cheque: Cheque) -> CloseDocData:
        """Печать чека"""
        if not self.shift.status():
            raise Exception("Смена не открыта!")
        if not self.kkt.status.document.condition == KKTStatus.Document.Condition.CLOSE:
            raise Exception("Открыт другой документ")
        self.kkt.open_doc(cheque.type)
        for item in cheque.items:
            self.kkt.add_item(item.title, "", item.count, item.price, item.tax, item.payment, item.subject)
        self.kkt.doc_payment(0, cheque.total)
        return self.kkt.close_doc(CutFlag.NONE)

    def print_egais(self):
        self.kkt.open_doc(DocumentType.SERVICE)
