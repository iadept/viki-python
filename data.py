from enum import Enum

from viki.packet import Input


class CutFlag:
    """Флаг отрезки при закрытии документа"""

    DEFAULT = "0"  # ??
    ONLY_SERVICE = "1"  # отрезка сервисных документов по завершению не выполняется
    NONE = "5"  # отрезка чеков продажи, покупки и возвратов по завершению не выполняется


class DocumentType(Enum):
    """Тип документа"""

    SERVICE = 1  # Сервисный документ
    SALE = 2  # Чек на продажу (приход)
    SALE_RETURN = 3  # Чек на возврат (возврат прихода)
    INTRODUCTION = 4  # Внесение в кассу
    COLLECTION = 5  # Инкассация
    PURCHASE = 6  # Чек на покупку (расход)
    PURCHASE_RETURN = 7  # Чек на возврат покупки (возврат расхода)


class TaxSystem(Enum):
    """Система налогообложения"""

    OVERALL = 0  # Общая
    SIMPLE_INCOME = 1  # Упрощенная Доход
    SIMPLE_INCOME_MINUS_EXPENSE = 2  # Упрощенная Доход минус Расход
    SINGLE_TAX = 3  # Единый налог на вмененный доход
    SINGLE_AGRICULTURE_TAX = 4  # Единый сельскохозяйственный налог
    PATENT_TAX = 5  # Патентная система налогообложения


class FontAttribute:
    """Аттрибуты текста при печати"""

    def __init__(self, number: int, double_height: bool = False, double_width: bool = False):
        self.result = number << 4
        if double_height:
            self.result = self.result & 1 << 4
        if double_width:
            self.result = self.result & 1 << 5

    def __str__(self):
        return str(self.result)


class BarcodeOut(Enum):
    """Параметры вывода заголовка штрих-кода"""
    NO = "0"  # Не вывдоить
    TOP = "1"  # Сверху
    BOTTOM = "2"  # Снизу
    TOP_BOTTOM = "3"  # Сверху и снизу


class BarcodeView(Enum):
    """Вид штрих-кода"""
    UPC_A = "0"
    UPC_E = "1"
    EAN_13 = "2"
    EAN_8 = "3"
    CODE_39 = "4"
    INTERLEAVED = "5"
    CODABAR = "6"
    PDF417 = "7"
    QR = "8"
    CODE_128 = "9"


class PaymentType(Enum):
    """Тип предоплаты"""
    PREPAY_FULL = "1"  # Предоплата 100%
    PREPAY = "2"  # Предоплата
    PREPAID = "3"  # Аванс
    FULL_SETTLEMENT = "4"  # Полный расчет
    PARTIAL_SETTLEMENT_AND_CREDIT = "5"  # Частичный расчет и кредит
    CREDIT_TRANSER = "6"  # Передача в кредит
    LOAN_PAYMENT = "7"  # Оплата кредита


class SubjectMatter(Enum):
    """Признак предмета расчета"""
    DEFAULT = "1"  # о реализуемом товаре, за исключением подакцизного товара
    EXCISE = "2"  # о реализуемом подакцизном товаре
    WORK = "3"  # о выполняемой работе
    SERVICE = "4"  # об оказываемой услуге
    RATES = "5"  # о приеме ставок при осуществлении деятельности по проведению азартных игр
    WINNINGS = "6"  # о выплате денежных средств в виде выигрыша при осуществлении деятельности по проведению азартных
    # игр

    # TODO Остальные


class ExtendErrorCode(Enum):
    NO_ERROR = 0  # Ошибок не было
    NO_BEGIN = 1  # Не была вызвана функция “Начало работы”
    NO_FISCAL_MODE = 2  # Нефискальный режим
    FN_ARCHIVE_CLOSE = 3  # Архив ФН закрыт
    FN_NO_REGISTERED = 4  # ФН не зарегистрирован
    FN_ALREADY_REGISTERED = 5  # ФН уже зарегистрирован
    NO_CHANGES_FOR_REGISTRATION = 7  # Нет изменений для перерегистрации ФН
    NO_DOC_OPEN = 8  # Документ не был открыт
    LAST_DOC_NO_CLOSED = 9  # Предыдущий документ не закрыт
    DOC_STATUS_NO_1 = 11  # Состояние документа не равно 1 (документ открыт, ввод позиций/печать текста)
    DOC_STATUS_NO_1_2 = 12  # Состояние документа не равно 1 или 2 (см. выше + была дана команда «Подытог»)
    DOC_STATUS_NO_1_2_3 = 13  # Состояние документа не равно 1 или 2 или 3 (см. выше + была дана вторая команда
    # «Подытог» либо начата оплата)
    DOC_STATUS_NO_4 = 14  # Состояние документа не равно 4 (расчёт завершён)
    DOC_NO_CLOSED_IN_FN = 15  # Документ закрыт в ФН
    DOC_NO_COMING = 16  # Документ не является продажей (приходом) или возвратом (возвратом прихода)
    DOC_NO_INTRODUCTION = 17  # Документ не является внесением или изъятием
    DOC_NO_SERVICE = 18  # Документ не является сервисным
    DOC_IS_SERVICE = 19  # Документ является сервисным
    SHIFT_NO_OPEN = 20  # Смена не открыта
    FN_ERROR_FATAL = 21  # Фатальная ошибка ФН
    FN_NO_IN_GET_MODE = 22  # ФН не в режиме получения документа для ОФД
    FN_EMPTY_OFD_ADDRESS = 23  # Не задан адрес сайта ФНС
    FN_EMPTY_OFD_TITLE = 24  # Не задано наименование ОФД
    FN_EMPTY_OFD_INN = 25  # Не задан ИНН ОФД
    DOC_ZERO_TOTAL = 26  # Нулевой итог документа
    DOC_EMPTY_PLACE = 27  # Не задано место расчетов
    DOC_EMPTY_AUTOMAT = 28  # Не задан номер автомата
    DOC_OVER_ONE_CREDIT = 29  # Попытка добавить больше одного предмета расчета с признаком способа расчёта "Оплата
    # кредита"
    DOC_EMPTY_EMAIL = 30  # Не задан email отправителя чека
    DOC_EMPTY_CASHIER = 33  # Не задано имя кассира
    OFD_HAS_UNSEND = 34  # Есть неотправленные в ОФД документы
    DOC_ONLY_ONE_DISCOUNT = 35  # Допустима только одна скидка на чек
    KKT_WRONG_REG_NUMBER = 37  # Неверный регистрационный номер
    KKT_ERROR_CHANGE_REG_DATA = 38  # Невозможно изменить регистрационные данные
    WRONG_DATETIME = 39  # Дата/время переданы неверно
    WRONG_TYPE_DOC = 40  # Неверный параметр "Тип документа"
    WRONG_DEPARTAMENT = 41  # Неверный параметр "Номер отдела"
    WRONG_NUMBER_DOC = 42  # Неверный параметр "Номер документа"
    WRONG_TAX_SYSTEM = 43  # Неверный параметр "Система налогообложения"
    WRONG_ITEM_TITLE = 44  # Неверный параметр "Название товара"
    WRONG_ITEM_ARTICLE = 45  # Неверный параметр "Артикул"
    WRONG_ITEM_COUNT = 46  # Неверный параметр "Количество товара"
    WRONG_ITEM_PRICE = 47  # Неверный параметр "Цена товара"
    WRONG_TAX_NUMBER = 48  # Неверный параметр "Номер ставки налога"
    WRONG_ITEM_NUMBER = 49  # Неверный параметр "Номер товарной позиции"
    WRONG_SECTION = 50  # Неверный параметр "Номер секции"
    WRONG_DISCOUNT_TITLE = 51  # Неверный параметр "Название скидки"
    WRONG_DISCOUNT_TOTAL = 52  # Неверный параметр "Сумма скидки"
    WRONG_SIGN_PAID_METHOD = 53  # Неверный параметр "Признак способа расчета"
    WRONG_SIGN_PAID_SUBJECT = 54  # Неверный параметр "Признак предмета расчета"
    WRONG_TYPE_PAID = 55  # Неверный параметр "Тип платежа"
    WRONG_TOTAL_PAID = 56  # Неверный параметр "Сумма платежа"
    WRONG_TEXT = 57  # Неверный параметр "Дополнительный текст"
    WRONG_ADDRESS_BUYER = 58  # Неверный параметр "Адрес покупателя"
    WRONG_FN_REPLACE = 59  # Неверный параметр "Замена ФН"
    WRONG_USER_INN = 60  # Неверный параметр "ИНН пользователя"
    WRONG_MODE = 61  # Неверный параметр "Режим работы"
    OFFLINE_MODE = 62  # Автономный режим и шифрование
    WRONG_AGENT_SIGN = 64  # Неверный признак агента
    WRONG_ACTIVATION_CODE = 65  # Неверный код активации
    WRONG_QUERY_NUMBER = 66  # Неверный номер запроса
    WRONG_PAID_NUMBER = 67  # Неверный номер платной услуги
    UPDATE_FOR_TABACCO = 68  # Обновите прошивку ККТ для работы с табачной продукцией
    MARK_TYPE_NOT_SUPPORT = 69  # Введённый тип маркировки не поддерживается
    UNIVERSAL_KEY_ACTIVATED = 70  # У вас активирован универсальный ключ
    WRONG_ADD_REQUISITE = 71  # Неверный параметр "Дополнительный реквизит чека"
    WRONG_ADD_REQUISITE_TITLE = 72  # Неверный параметр "Наименование дополнительного реквизита пользователя"
    WRONG_ADD_REQUISITE_VALUE = 73  # Неверный параметр "Значение дополнительного реквизита пользователя"
    FFD_NON_ACTIVATED = 74  # Услуга ФФД 1.1 не активирована


class KKTStatus:
    """Флаги статуса ККТ"""

    class Fatal:
        """Статус фатального состояния ККТ"""

        def __init__(self, source):
            self.nvr_crc = source & 1 << 0 != 0  # Неверная контрольная сумма NVR
            self.conf_crc = source & 1 << 1 != 0  # Неверная котрольная сумма в конфигурации
            self.no_link = source & 1 << 2 != 0  # Нет связи с ФН
            self.reversed1 = source & 1 << 3 != 0  # Зарезервировано
            self.reversed2 = source & 1 << 4 != 0  # Зарезервировано
            self.no_authorized = source & 1 << 5 != 0  # ККТ не авторизовано
            self.fn = source & 1 << 6 != 0  # Фатальная ошибка ФН
            self.reversed2 = source & 1 << 7 != 0  # Зарезервировано
            self.sd_card = source & 1 << 8 != 0  # SD карта отсутствует или неисправна

        def check(self) -> bool:
            for field in self.__dict__:
                if not field:
                    return False
            return True

    class Current:
        """Статус текущих флагов ККТ"""

        def __init__(self, source):
            self.no_begin = source & 1 << 0 != 0  # Не была вызвана функция “Начало работы”
            self.no_fiscal = source & 1 << 1 != 0  # Нефискальный режим
            self.shift_open = source & 1 << 2 != 0  # Смена открыта
            self.shift_more_24 = source & 1 << 3 != 0  # Смена больше 24 часов
            self.archive_close = source & 1 << 4 != 0  # Архив ФН закрыт
            self.fn_no_reg = source & 1 << 5 != 0  # ФН не зарегистрирован
            self.reversed1 = source & 1 << 6 != 0  # Зарезервировано
            self.reversed2 = source & 1 << 7 != 0  # Зарезервировано
            self.error_shift_close = source & 1 << 8 != 0  # Не было завершено закрытие смены
            self.tape_error = source & 1 << 8 != 0  # Ошибка контрольной ленты

    class Document:
        """Статус документа"""

        class Type(Enum):
            CLOSE = 0  # документ закрыт
            SERVICE = 1  # сервисный документ
            COMING = 2  # чек на продажу (приход)
            COMING_RETURN = 3  # чек на возврат (возврат прихода)
            INTRODUCTION = 4  # внесение в кассу
            COLLECTION = 5  # инкассация
            PURCHASE = 6  # чек на покупку (расход)
            PURCHASE_RETURN = 7  # чек на возврат покупки (возврат расхода)

        class Condition(Enum):
            CLOSE = 0  # документ закрыт
            OPEN = 1  # устанавливается после команды "открыть документ"
            # (Для типов документа 2 и 3 можно добавлять товарные позиции)
            SUBTOTAL = 2  # Устанавливается после первой команды "Подытог"
            PAYMENT = 3  # Устанавливается после второй команды "Подытог" или после начала команды "Оплата"
            COMPLETE = 4  # Расчет завершен, требуется закрыть документ
            CLOSE_NO_COMPLETE = 8  # Команда закрытия документа была дана в ФН, но документ не был завершен

        def __init__(self, source):
            self.type = KKTStatus.Document.Type(source >> 4)
            self.condition = KKTStatus.Document.Condition(source & 0x0F)

    def __init__(self, fatal, current, document):
        self.fatal = KKTStatus.Fatal(fatal)
        self.current = KKTStatus.Current(current)
        self.document = KKTStatus.Document(document)


class PrinterStatus:
    """
    Статус печатающего устройства
    """

    def __init__(self, status):
        self.no_ready = status & 1 << 0 != 0  # Принтер не готов
        self.no_paper = status & 1 << 1 != 0  # В принтере нет бумаги
        self.open_cover = status & 1 << 2 != 0  # Открыта крышка принтера
        self.error_cutter = status & 1 << 3 != 0  # Ошибка резчика принтера
        self.no_link = status & 1 << 7 != 0  # Нет связи с принтером


class FNStatus:
    """
    Состояние ФН
    """

    class Phase(Enum):
        SETTING = 0  # Настройка
        READY = 1  # Готовность к фискализации
        FISKAL = 3  # Фискальный режим
        POSTFISKAL = 7  # Постфиксальный режим. Идет передача ФД в ОФД
        READ_ARCHIVE = 15  # Чтение данных из архива ФН

    def __init__(self, source: int):
        self.phase = FNStatus.Phase(source >> 4)  # Фаза жизни ФН
        self.document = source & 1 << 5 != 0  # Получены данные документа
        self.shift = source & 1 << 6 != 0  # Смена открыта


class FNShiftStatus:
    """
    Cостояние текущей смены
    """

    def __init__(self, number, is_open, cheque):
        self.number = number  # Номер смены
        self.is_open = is_open  # Cмена открыта
        self.cheque = cheque  # Номер чека в смене


class FNOFDStatus:
    """
    Cостояние обмена с ОФД
    """

    def __init__(self, status, count, number, date):
        self.connected = status & 1 << 0 != 0  # Транспортное соединение установлено
        self.has_message = status & 1 << 1 != 0  # Есть сообщение для передачи в ОФД
        self.wait_meassage = status & 1 << 2 != 0  # Ожидание ответного сообщения (квитанции) от ОФД
        self.has_command = status & 1 << 3 != 0  # Есть команда от ОФД
        self.change_settings = status & 1 << 4 != 0  # Изменились настройки соединения с ОФД
        self.wait_answer = status & 1 << 5 != 0  # Ожидание ответа на команду от ОФД
        self.read_message = status & 1 << 6 != 0  # Начато чтение сообщения для ОФД

        self.count = count  # Количество документов для передачи в ОФД
        self.number = number  # Номер первого документа для передачи в ОФД
        self.date = date  # Дата/время первого док-та для передачи в ОФД


class CloseDocData:
    """Ответ команды завершения документа"""

    def __init__(self, packet: Input):
        self.number = packet.to_int(0)  # Сквозной номер документа
        self.counter = packet.to_string(1)  # Операционный счетчик
        self.string_fd_fp = packet.to_string(2)  # Строка ФД и ФП
        self.number_fd = packet.to_int(3)  # ФД - номер фискального документа
        self.fp_sign = packet.to_int(4)  # ФП - фискальный признак
        self.shift_number = packet.to_int(5)  # Номер смены
        self.number_doc_in_shift = packet.to_int(6)  # Номер документа в смене
        self.date = packet.to_string(7)  # Дата документа
        self.time = packet.to_string(8)  # Время документа

