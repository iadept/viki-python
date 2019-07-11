from dataclasses import dataclass
from datetime import datetime
from serial import Serial

from viki.data import FNStatus, FNShiftStatus, FNOFDStatus, KKTStatus, PrinterStatus, ExtendErrorCode, CloseDocData,\
    BarcodeOut, BarcodeView, FontAttribute, DocumentType, TaxSystem, PaymentType, SubjectMatter, \
    CutFlag
from viki.packet import Input, Output, Command


class KKTAccess:
    """Базовы класс для абстракций"""

    def __init__(self, kkt: 'KKT'):
        self.kkt: KKT = kkt


class Register(KKTAccess):
    """
    Значения сменных счетчиков и регистров ККТ
    """

    @property
    def current_shift(self) -> int:
        """Вернуть номер текущей смены"""
        return self.kkt.send(Output(0x01).add_param("1")).to_int(1)

    @property
    def number_next_cheque(self) -> int:
        """Вернуть номер следующего чека"""
        return self.kkt.send(Output(0x01).add_param("2")).to_int(1)

    # TODO Остальные регистры


class InformationData(KKTAccess):
    """Запрос сведений о ККТ"""

    @property
    def manufacture_number(self) -> str:
        """Вернуть заводской номер ККТ"""
        return self.kkt.send(Output(0x02).add_param("1")).to_string(1)

    @property
    def firmware_id(self) -> int:
        """Вернуть идентификатор прошивки"""
        return self.kkt.send(Output(0x02).add_param("2")).to_int(1)

    @property
    def inn(self) -> str:
        """Вернуть ИНН"""
        return self.kkt.send(Output(0x02).add_param("3")).to_string(1)

    @property
    def registration_number(self) -> str:
        """Вернуть регистрационный номер ККТ"""
        return self.kkt.send(Output(0x02).add_param("4")).to_string(1)

    @property
    def datetime_last_operation(self) -> datetime:
        """Вернуть дату и время последней фискальной операции"""
        return self.kkt.send(Output(0x02).add_param("5")).to_datetime(1, 2)

    @property
    def datetime_last_registration(self) -> datetime:
        """Вернуть дату регистрации / перерегистрации"""
        return self.kkt.send(Output(0x02).add_param("6")).to_date(1)

    @property
    def cashbox_total(self) -> str:
        """Вернуть сумму наличных в денежном ящике"""
        # TODO Float!!
        return self.kkt.send(Output(0x02).add_param("7")).to_string(1)

    @property
    def number_next_document(self) -> int:
        """Вернуть номер следующего документа"""
        return self.kkt.send(Output(0x02).add_param("8")).to_int(1)

    @property
    def number_shift(self) -> int:
        """Вернуть номер смены регистрации"""
        return self.kkt.send(Output(0x02).add_param("9")).to_int(1)

    @property
    def number_next_x_report(self) -> int:
        """Вернуть номер следующего X отчета"""
        return self.kkt.send(Output(0x02).add_param("10")).to_int(1)

    @property
    def current_counter(self) -> str:
        """Вернуть текущий операционный счетчик"""
        return self.kkt.send(Output(0x02).add_param("11")).to_string(1)

    # TODO 12-24

    @property
    def transition_nds(self) -> bool:
        """Вернуть состояние перехода на НДС 20%"""
        return self.kkt.send(Output(0x02).add_param("40")).to_bool(1)

    @property
    def work_firmware_id(self) -> str:
        """Вернуть рабочий идентификатор прошивки"""
        return self.kkt.send(Output(0x02).add_param("70")).to_string(1)

    @property
    def firmware_build(self) -> str:
        """Вернуть версию билда прошивки"""
        return self.kkt.send(Output(0x02).add_param("71")).to_string(1)


class ChequeData(KKTAccess):
    """
    Данные по чеку.
    """

    @dataclass
    class Counter:
        """
        Cчетчики текущего документа
        """
        total: int  # Cумма чека
        discount: int  # Cумма скидки по чеку

    @dataclass
    class Data:
        """
        Данные по последнему закрытому чеку
        """
        type: int
        counter: str
        number_cheque: int
        number_document: int
        total: str
        discount: str
        fp: str
        number_fd: int

    @property
    def current(self) -> Counter:
        """Вернуть счетчики текущего документа"""
        packet = self.kkt.send(Output(0x03).add_param('1'))
        return ChequeData.Counter(packet.to_string(1), packet.to_string(2))

    @property
    def last(self):
        packet = self.kkt.send(Output(0x03).add_param('2'))
        return ChequeData.Data(packet.to_int(1),
                               packet.to_string(2),
                               packet.to_int(3),
                               packet.to_int(4),
                               packet.to_string(5),
                               packet.to_string(6),
                               packet.to_string(8),
                               packet.to_int(9))


class ServiceData(KKTAccess):
    """
    Разнообразная сервисная информация о ККТ
    """

    @property
    def battery(self) -> int:
        """Вернуть напряжение на батарейке (мВ)"""
        return self.kkt.send(Output(0x05).add_param("7")).to_int(1)

    @property
    def type(self) -> str:
        """Вернуть тип ПУ"""
        return self.kkt.send(Output(0x05).add_param("10")).to_string(1)

    @property
    def version(self) -> str:
        """Вернуть версию BIOS ПУ"""
        return self.kkt.send(Output(0x05).add_param("11")).to_string(1)

    @property
    def serial(self) -> str:
        """Вернуть серийный номер ПУ"""
        return self.kkt.send(Output(0x05).add_param("12")).to_string(1)


class ExtendErrorData(KKTAccess):
    """Данные по ошибкам ФН и ККТ"""

    class BlockFN:
        """Статус блокировок по ФН"""

        def __init__(self, source):
            self.reversed1 = source & 1 << 0 != 0  # Зарезервировано
            self.fn_not_found = source & 1 << 1 != 0  # ФН не найден
            self.archive_no_closed = source & 1 << 2 != 0  # Не был закрыт архив ФН
            self.archive_test_error = source & 1 << 3 != 0  # Ошибка теста архива ФН
            self.error_link_fn = source & 1 << 4 != 0  # Ошибка связи с ФН
            self.no_shift_close = source & 1 << 5 != 0  # Не завершена операция закрытия смены
            self.reversed2 = source & 1 << 6 != 0  # Зарезервировано
            self.fn_fill = source & 1 << 7 != 0  # ФН заполнен

    @property
    def code(self) -> (ExtendErrorCode, str):
        """Вернуть расширенный код ошибки"""
        packet = self.kkt.send(Output(0x06).add_param('1'))
        return ExtendErrorCode(packet.to_int(1)), packet.to_string(2)

    @property
    def block(self) -> BlockFN:
        """Вернуть статус блокировок по ФН"""
        packet = self.kkt.send(Output(0x06).add_param('1'))
        return ExtendErrorData.BlockFN(packet.to_int(1))


class SettingsData(KKTAccess):
    """Настройки ККТ"""

    class Printer:
        """Параметры ПУ"""

        def __init__(self, source):
            self.small_spacing = source & 1 << 0 != 0  # Печать с уменьшенным межстрочным интервалом
            self.full_cut = source & 1 << 1 != 0  # Полная отрезка
            self.print_logo = source & 1 << 2 != 0  # Печатать логотип
            self.print_qr = source & 1 << 5 != 0  # Печатать QR код на чеке (неотключаемая настройка)
            self.print_departament = source & 1 << 6 != 0  # Печатать отделы на чеках
            self.no_print_doc = source & 1 << 7 != 0  # Не печатать документы на чековой ленте

        def value(self) -> int:
            result = 0
            if self.no_print_doc:
                result = result | 1 << 7
            if self.print_departament:
                result = result | 1 << 6
            if self.print_qr:
                result = result | 1 << 5
            if self.print_logo:
                result = result | 1 << 2
            if self.full_cut:
                result = result | 1 << 1
            if self.small_spacing:
                result = result | 1 << 0
            return result

    class Cheque:
        """Параметры чека"""

        def __init__(self, source):
            self.design = source >> 4  # Номер дизайна чека: 0 - обычный
            self.no_print_dia = source & 1 << 6 != 0  # Не печатать наличные в ДЯ на чеках внесения/инкассации
            self.external_counter = source & 1 << 7 != 0  # Нумерация чеков внешней программой

        def value(self) -> int:
            result = self.design << 4
            if self.no_print_dia:
                result = result | 1 << 6
            if self.external_counter:
                result = result | 1 << 7
            return result

    class ReportCloseShift:
        """Параметры отчета о закрытии смены"""

        def __init__(self, source):
            self.cumulative_total_on_begin = source & 1 << 0 != 0  # Печатать сумму нарастающего итога на начало смены
            self.cumulative_total = source & 1 << 1 != 0  # Печатать суммы нарастающего итога
            self.pending_cheque = source & 1 << 2 != 0  # Печатать информацию об отложенных чеках
            self.discount_info = source & 1 << 3 != 0  # Печатать информацию о скидках
            self.cashbox_action = source & 1 << 4 != 0  # Печатать информацию об операциях с денежным ящиком
            self.unused_cash = source & 1 << 5 != 0  # Не печатать информацию по неиспользованным за смену платежным
            # средствам
            self.datetime = source & 1 << 6 != 0  # Печатать дату и время начала смены
            self.section = source & 1 << 7 != 0  # Печатать секции на отчете

        def value(self) -> int:
            result = 0
            if self.cumulative_total_on_begin:
                result = result | 1 << 0
            if self.cumulative_total:
                result = result | 1 << 1
            if self.pending_cheque:
                result = result | 1 << 2
            if self.discount_info:
                result = result | 1 << 3
            if self.cashbox_action:
                result = result | 1 << 4
            if self.unused_cash:
                result = result | 1 << 5
            if self.datetime:
                result = result | 1 << 6
            if self.section:
                result = result | 1 << 7
            return result

    class AccountManagement:
        """Управление расчетами"""

        def __init__(self, source):
            self.disable_control_cashbox = source & 1 << 0 != 0  # Контроль наличных в денежном ящике отключен
            self.no_consider_cancel_cheque = source & 1 << 1 != 0  # Учитывать чеки, аннулированные при включении
            # питания
            self.auto_collection = source & 1 << 2 != 0  # Автоматическая инкассация включена
            self.counters = source & 1 << 3 != 0  # Счетчики покупок(расходов) включены
            self.print_ckl = source & 1 << 4 != 0  # Автоматическая печать СКЛ включена
            self.ckl = source & 1 << 5 != 0  # СКЛ включена
            self.print_total = source & 1 << 6 != 0  # Печать суммы нарастающего итога продаж/покупок на X-отчетах и
            # отчетах о закрытии смены включена.
            self.print_total_return = source & 1 << 7 != 0  # Печать суммы нарастающего итога возвратовна X-отчетах и
            # отчетах о закрытии смены х включена

        def value(self) -> int:
            result = 0
            if self.disable_control_cashbox:
                result = result | 1 << 0
            if self.no_consider_cancel_cheque:
                result = result | 1 << 1
            if self.auto_collection:
                result = result | 1 << 2
            if self.counters:
                result = result | 1 << 3
            if self.print_ckl:
                result = result | 1 << 4
            if self.ckl:
                result = result | 1 << 5
            if self.print_total:
                result = result | 1 << 6
            if self.print_total_return:
                result = result | 1 << 7
            return result

    class TaxManagement:
        """Управление расчетами и печатью налогов"""

        def __init__(self, source):
            self.print_tax_on_report = source & 1 << 0 != 0  # Печатать налоги на отчетах
            self.print_tax_on_cheque = source & 1 << 1 != 0  # Печатать налоги на чеках
            self.print_zero_tax_on_report = source & 1 << 2 != 0  # Печатать нулевые налоговые суммы на отчетах
            self.round_tax_after_enter_discount = source & 1 << 3 != 0  # Округлять сумму налога только после ввода всех
            # позиций и скидок
            self.charge_nds = source & 1 << 6 != 0  # НДС к стоимости товарной позиции

        def value(self) -> int:
            result = 0
            if self.print_tax_on_report:
                result = result | 1 << 0
            if self.print_tax_on_cheque:
                result = result | 1 << 1
            if self.print_zero_tax_on_report:
                result = result | 1 << 2
            if self.round_tax_after_enter_discount:
                result = result | 1 << 3
            if self.charge_nds:
                result = result | 1 << 6
            return result

    @property
    def printer(self) -> Printer:
        """Параметры ПУ"""
        return SettingsData.Printer(self.kkt.send(Output(0x11).add_param('1').add_param('0')).to_int(0))

    @printer.setter
    def printer(self, value: Printer):
        self.kkt.send(Output(0x12).add_param("1").add_param('0').add_param(str(value.value())))

    @property
    def cheque(self) -> Cheque:
        """Параметры Чека"""
        return SettingsData.Cheque(self.kkt.send(Output(0x11).add_param('2').add_param('0')).to_int(0))

    @cheque.setter
    def cheque(self, value: Cheque):
        self.kkt.send(Output(0x12).add_param("2").add_param('0').add_param(str(value.value())))

    @property
    def report_close_shift(self) -> ReportCloseShift:
        """Параметры отчета о закрытии смены """
        return SettingsData.ReportCloseShift(self.kkt.send(Output(0x11).add_param('3').add_param('0')).to_int(0))

    @report_close_shift.setter
    def report_close_shift(self, value: ReportCloseShift):
        self.kkt.send(Output(0x12).add_param("3").add_param('0').add_param(str(value.value())))

    @property
    def open_cash_box(self) -> bool:
        return self.kkt.send(Output(0x11).add_param('4').add_param('0')).to_bool(0)

    @open_cash_box.setter
    def open_cash_box(self, value):
        self.kkt.send((Output(0x12).add_param("4").add_param("0").add_param(value)))

    @property
    def account_management(self) -> AccountManagement:
        return SettingsData.AccountManagement(self.kkt.send(Output(0x11).add_param('5').add_param('0')).to_int(0))

    @account_management.setter
    def account_management(self, value: AccountManagement):
        self.kkt.send(Output(0x12).add_param("5").add_param('0').add_param(str(value.value())))

    @property
    def tax_management(self) -> TaxManagement:
        return SettingsData.TaxManagement(self.kkt.send(Output(0x11).add_param('6').add_param('0')).to_int(0))

    @tax_management.setter
    def tax_management(self, value: TaxManagement):
        self.kkt.send(Output(0x12).add_param("6").add_param('0').add_param(str(value.value())))

    @property
    def kkt_number(self) -> int:
        return self.kkt.send(Output(0x11).add_param('10').add_param('0')).to_int(0)

    @kkt_number.setter
    def kkt_number(self, value):
        self.kkt.send((Output(0x12).add_param("10").add_param("0").add_param(value)))

    # TODO 11-54

    @property
    def number_automat(self) -> str:
        """Номер автомата"""
        return self.kkt.send(Output(0x11).add_param('70').add_param('0')).to_string(0)

    @property
    def inn_ofd(self) -> str:
        """ИНН ОФД"""
        return self.kkt.send(Output(0x11).add_param('71').add_param('0')).to_string(0)

    @property
    def content_qr_code(self) -> str:
        """Содержание QR-кода"""
        return self.kkt.send(Output(0x11).add_param('72').add_param('0')).to_string(0)

    @property
    def ip(self) -> str:
        """IP-адрес ККТ"""
        return self.kkt.send(Output(0x11).add_param('73').add_param('0')).to_string(0)

    @ip.setter
    def ip(self, value):
        """IP-адрес ККТ"""
        self.kkt.send((Output(0x12).add_param("73").add_param("0").add_param(value)))

    @property
    def mask(self) -> str:
        """Маска подсети"""
        return self.kkt.send(Output(0x11).add_param('74').add_param('0')).to_string(0)

    @mask.setter
    def mask(self, value):
        """Маска подсети"""
        self.kkt.send((Output(0x12).add_param("74").add_param("0").add_param(value)))

    @property
    def gateway(self) -> str:
        """IP-адрес шлюза"""
        return self.kkt.send(Output(0x11).add_param('75').add_param('0')).to_string(0)

    @gateway.setter
    def gateway(self, value):
        """IP-адрес шлюза"""
        self.kkt.send((Output(0x12).add_param("75").add_param("0").add_param(value)))

    @property
    def dns(self) -> str:
        """IP-адрес DNS"""
        return self.kkt.send(Output(0x11).add_param('76').add_param('0')).to_string(0)

    @dns.setter
    def dns(self, value):
        """IP-адрес DNS"""
        self.kkt.send((Output(0x12).add_param("76").add_param("0").add_param(value)))

    @property
    def ofd_address(self) -> str:
        """Адрес сервера ОФД для отправки документов"""
        return self.kkt.send(Output(0x11).add_param('77').add_param('0')).to_string(0)

    @ofd_address.setter
    def ofd_address(self, value):
        """Адрес сервера ОФД для отправки документов"""
        self.kkt.send((Output(0x12).add_param("77").add_param("0").add_param(value)))

    @property
    def ofd_port(self) -> int:
        """Порт сервера ОФД"""
        return self.kkt.send(Output(0x11).add_param('78').add_param('0')).to_int(0)

    @ofd_port.setter
    def ofd_port(self, value):
        """Порт сервера ОФД"""
        self.kkt.send((Output(0x12).add_param("78").add_param("0").add_param(value)))


class ExchangeFNData(KKTAccess):

    @property
    def reg_number(self) -> str:
        """Вернуть регистрационный номер ФН"""
        return self.kkt.send(Output(0x78).add_param('1')).to_string(1)

    @property
    def status(self) -> FNStatus:
        """Вернуть статус ФН"""
        return FNStatus(self.kkt.send(Output(0x78).add_param('2')).to_int(1))

    @property
    def number_last_doc(self) -> str:
        """Вернуть номер последнего фискального документа"""
        return self.kkt.send(Output(0x78).add_param('3')).to_string(1)

    @property
    def reg_datetime(self):
        """Вернуть дату и время регистрации"""
        packet = self.kkt.send(Output(0x78).add_param("4"))
        return packet.to_datetime(1, 2)

    @property
    def last_reg_number(self):
        """Вернуть номер ФД последней регистрации"""
        return self.kkt.send(Output(0x78).add_param('5')).to_int(1)


    @property
    def shift_status(self) -> FNShiftStatus:
        """Вернуть состояние текущей смены"""
        packet = self.kkt.send(Output(0x78).add_param('6'))
        return FNShiftStatus(packet.to_string(1), packet.to_bool(2), packet.to_string(3))

    @property
    def exchange_status(self) -> FNOFDStatus:
        """Вернуть состояние обмена с ОФД"""
        packet = self.kkt.send(Output(0x78).add_param('7'))
        print(packet)
        return FNOFDStatus(packet.to_int(1), packet.to_string(2), packet.to_string(3), packet.to_datetime(4, 5))

    # TODO 11-19

class KKT:

    def __init__(self,
                 port: str,
                 operator_inn: str,
                 operator: str,
                 tax_system: TaxSystem,
                 password: str = "PIRI"):
        if len(operator) == 0:
            raise Exception("Имя оператора не может быть пустым")
        self.operator = operator_inn + "&" + operator
        self.tax_system = str(tax_system.value)
        if len(password) != 4:
            raise Exception("Password length may be 4!")
        self.__pasword = password
        self.port = Serial(port=port, baudrate=57600)
        if not self.check_link():
            raise Exception("Нет связи с кассой!")
        self.info = Info(self)

    def send_command(self, code) -> Input:
        """
        Отправляет команду с заданным кодом на сервер
        :param code: код команды
        :return:
        """
        return self.send(Output(code))

    def send(self, packet: Output) -> Input:
        if not self.check_link():
            raise Exception("Нет связи!")
        data = packet.get_bytes(self.__pasword, 0x30)
        #print(" ".join("%02X" % x for x in data))
        self.port.write(data)
        result = Input(self.port)
        if result.error:
            raise Exception(result.error)
        return result

    def scout_paper(self):
        """
        Промотка бумаги
        """
        self.send_command(0x0A)

    def check_link(self):
        """
        Проверка связи
        Если в момент проверки связи ККТ передает данные в ответ на другую команду, то ответ может быть получен только
        после завершения этой передачи
        """
        self.port.write([0x05])
        return ord(self.port.read(1)) == 6

    def cancel(self):
        """
        Прервать выполнение отчета
        Все отчеты, кроме X или отчета о закрытии, могут быть прерваны
        """
        self.send_command(0x18)

    @property
    def status(self) -> KKTStatus:
        """Команда возвращает статус фатального состояния ККТ, статус текущих флагов ККТ и статус документа"""
        packet = self.send(Output(0x00))
        return KKTStatus(packet.to_int(0), packet.to_int(1), packet.to_int(2))

    @property
    def register(self) -> Register:
        """Команда возвращает статус фатального состояния ККТ, статус текущих флагов ККТ и статус документа"""
        return Register(self)

    @property
    def information(self) -> InformationData:
        """Эта команда позволяет получать разнообразную информацию о ККТ"""
        return InformationData(self)

    @property
    def cheque(self) -> ChequeData:
        """Эта команда позволяет получать данные по чеку."""
        return ChequeData(self)

    @property
    def printer(self) -> PrinterStatus:
        """Эта команда позволяет получать состояние печатающего устройства"""
        return PrinterStatus(self.send_command(0x04).to_int(0))

    @property
    def service(self) -> ServiceData:
        """Эта команда позволяет получать разнообразную сервисную информацию о ККТ"""
        return ServiceData(self)

    @property
    def error(self) -> ExtendErrorData:
        """Эта команда позволяет получать данные по ошибкам ФН и ККТ."""
        return ExtendErrorData(self)

    def begin(self, host_datetime=datetime.now()):
        """
        Начало работы с кассой
        :param host_datetime: Время управляющего компьютера
        """
        query = Output(0x10)
        query.add_param(host_datetime)
        self.send(query)

    @property
    def settings(self) -> SettingsData:
        """Настройки ККТ"""
        return SettingsData(self)

    @property
    def datetime(self) -> datetime:
        """Возвращает дату и время ККМ"""
        return self.send_command(0x13).to_datetime(0, 1)

    @datetime.setter
    def datetime(self, value: datetime):
        """Эта команда позволяет устанавливать новые время и дату ККТ, при условии закрытой смены"""
        str_date = value.strftime("%d%m%y")
        str_time = value.strftime("%H%M%S")
        self.send(Output(0x14).add_param(str_date).add_param(str_time))

    # TODO 15 и 16 Работа с логотипом, в последную очередь)

    def report_x(self):
        """Сформировать отчет без гашения (X-отчет)"""
        self.send(Output(0x20).add_param(self.operator))

    def close_shift(self):
        """Сформировать отчет о закрытии смены"""
        # TODO Параметр (Целое число) Опции отчета в документации ничего=(
        self.send(Output(0x21).add_param(self.operator).add_param("0"))

    def open_shift(self):
        """Открыть смену"""
        self.send(Output(0x23).add_param(self.operator))

    # TODO 24 Установить дополнительные реквизиты позиции

    def open_doc(self,
                 doc_type: DocumentType,
                 mode_bulk: bool = False,
                 mode_delay: bool = False,
                 departament: int = 0,
                 number: int = 0):
        """
        Открыть документ

        В пакетном режиме формирования документа, при успешном выполнении команд формирования чека
        - (Не реализовано) Установить дополнительные реквизиты позиции
        - print_text: Печать текста
        - print_barcode: Печатать штрих-код
        - add_item: Добавить товарную позицию
        - doc_subtotal: Подытог
        - Скидка на чек
        - doc_payment: Оплата
        - Внесение / изъятие суммы
        - Печать реквизита
        - Сравнить сумму по чеку
        , ответ на команду не посылается. Если какая-либо команда выполняется с ошибкой, то на нее возвращается
        стандартный ответ с кодом ошибки. Последующие команды формирования чека игнорируются, на каждую такую комадну
        возвращается стандартный ответ с кодом ошибки "Функция невыполнима при данном статусе ККТ" до поступления команд
         “Завершить документ” или “Аннулировать документ”.

        При возникновении ошибки в процессе наполнения документа в пакетном режиме необходимо аннулировать документ и
        полностью сформировать документ заново, начиная с команды "Открыть документ".

        :param doc_type: Тип документа
        :param mode_bulk: Пакетный режим формирования документа
        :param mode_delay: Режим отложенной печати реквизитов
        :param departament: Номер отдела (1-99)
        :param number: Номер документа
        """
        param = doc_type.value
        if mode_bulk:
            param = param & 1 << 4
        if mode_delay:
            param = param & 1 << 5
        query = Output(0x30)
        query.add_param(str(param))
        query.add_param(str(departament))
        query.add_param(self.operator)
        if number == 0 and self.settings.cheque.external_counter:
            raise Exception("Настроена внешняя нумерация чеков, необходимо передавать номер документа!")
        query.add_param(str(number))
        query.add_param(self.tax_system)
        self.send(query)

    def close_doc(self, cut: CutFlag, sign_internet_payment: bool = None, address: str = None, title: str = None,
                  value: str = None, buyer: str = None, buyer_inn: str = None) -> CloseDocData:
        """
        Завершить документ

        Фискальный признак возвращается только при завершении чеков на приход, возврат прихода, расход и возврат
        расхода. В пакетном режиме формирования документа, команда “Завершить документ” выключает пакетный режим.
        Если в пакетном режиме ошибка возникла ранее команды “Завершить документ”, то ответ команду “Завершить документ”
        не возвращается. Можно продолжить формирование документа, начиная с команды вернувшей ошибку, обычном режиме.

        :param cut: флаг отрезки документов
        :param sign_internet_payment: установить признак расчетов в интернет
        :param address: адрес покупателя # TODO Email?
        :param title: название дополнительного реквизита пользователя
        :param value: значение дополнительного реквизита пользователя
        :param buyer: покупатель
        :param buyer_inn: ИНН покупателя
        :return:
        """
        query = Output(0x31)
        query.add_param(cut)
        if address:
            query.add_param(address)
        if sign_internet_payment:
            query.add_param(sign_internet_payment)
        if title:
            query.add_param(title)
        if value:
            query.add_param(value)
        if buyer:
            query.add_param(buyer)
        if buyer_inn:
            query.add_param(buyer_inn)
        packet = self.send(query)
        return CloseDocData(packet)

    def cancel_doc(self):
        """
        Эта команда прерывает формирование текущего документа, данные удаляются из оперативной памяти ККТ и
        печатается сообщение об аннулировании
        """
        self.send(Output(0x32))

    def postpone_doc(self, cause: str):
        """
        Эта команда работает аналогично команде “Аннулировать документ”, но подается в случаях, когда документ
        отменяется не навсегда, а будет обязательно повторно введен, в течении данной смены. Данные документа удаляются
        из оперативной памяти ККТ и печатается причина отказа от чека.

        Используя параметры печати отчета о закрытии смены в “Таблица настроек ККТ”, можно настроить в отчете о закрытии
        печать информации по отложенным за смену чекам. При этом, если команда "Отложить чек" выполняется без параметра
        (пустая строка), то такие чеки учитываются в отчете о закрытии, если с параметром – не учитываются.
        :param cause: Причина отказа от чека (Длина 40 символов)
        """
        if len(cause) > 40:
            raise Exception("Неверная длина причины отказа")
        self.send(Output(0x33).add_param(cause))

    def cut_doc(self):
        """
        Эта команда выполняет принудительную отрезку документа с предпечатью.
        """
        self.send_command(0x34)

    def print_text(self, text: str, font: FontAttribute):
        """
        C помощью данной команды печатается текст внутри открытого сервисного документа
        :param text: Текст
        :param font: Атрибуты текста
        """
        self.send(Output(0x40).add_param(text).add_param(str(font)))

    def print_barcode(self, out: BarcodeOut, width, height, view: BarcodeView, text):
        """
        С помощью данной команды можно распечатать штрих-код товара.
        Заметка:
            EAN-13 у меня печатаеться только с шириной 2 или 3 О_о
        :param out: Заголовок
        :param width: Ширина штрих-кода - значение задается в точках и может быть от 2 до 8
        :param height: Высота штрих-кода - значение задается в точках и может принимать значения от 1 до 255
        :param view: Тип штрих-кода - Определяет, какой штрих-код будет напечатан
        :param text: Штрих-код- строка содержащая штрих-код
        """
        if self.status.current.no_begin:
            raise Exception("Вызовите начало работы!")
        self.send(Output(0x41).add_param(out.value).add_param(str(width)).add_param(str(height)).add_param(
            view.value).add_param(text))

    def add_item(self, title: str, article: str, count: float, price: float, number_tax: int,
                 payment_type: PaymentType, subject_matter: SubjectMatter,
                 discount_total: float = 0, number_item: str = "", number_departament: int = 0,
                 code_country: str = None, number_customs: str = None, excise_total: float = None):
        """
        Добавить товарную позицию

        Эта команда может быть вызвана сразу после открытия чека и может повторяться любое количество раз (если признак
        способа расчета не равен 7) внутри текущего документа для отражения всего списка товаров. Если позиция не может
        быть добавлена в ФН, на чеке после данных о позиции печатается строка “ОПЕРАЦИЯ ОТМЕНЕНА” и возвращается
        соответствующий код ошибки ФН.

        Для повышения точности вычислений, можно передавать количество с точностью до 9 знаков после запятой, при этом в
        умножении на цену будет участвовать 9 знаков после запятой, а печататься только первые 3.

        Сумма позиции, получаемая в результате умножения цены на количество, округляется к ближайшему целому, т.е. часть
        менее 0.5 коп отбрасывается, 0.5 коп и более округляется до 1 коп.

        Параметры ”Номер товарной позиции” и “Номер секции” не являются обязательными и могут отсутствовать. Если номер
        секции отсутствует (или равен нулю), учет ведется на номер отдела, указанный при открытии документа. Номер
        позиции - символьное поле, состоящее из цифр и символа разделителя, которым может быть пробел, двоеточие, тире и
         другие символы.

        В связи с требованиями ФФД поле "Название товара" при длине, большей 128 символов, будет обрезано до 128
        символов.
        :param title: название товара(0..224)
        :param article: артикул или штриховой код товара/номер ТРК
        :param count: количество товара в товарной позиции
        :param price: цена товара по данному артикулу
        :param number_tax: номер ставки налога (Номер налога в регистре кассы обычно (1-20%, 2-10%, 3-Без НДС или 0%))
        :param number_item: номер товарной позиции
        :param number_departament: номер секции
        :param discount_total: сумма скидки
        :param payment_type: признак способа расчета
        :param subject_matter: признак предмета расчета
        :param code_country: код страны происхождения товара (номер)
        :param number_customs: номер таможенной декларации
        :param excise_total: сумма акциза
        :return:
        """
        query = Output(0x42)
        query.add_param(title)
        query.add_param(article)
        query.add_param("%0.3f" % count)
        query.add_param("%0.3f" % price)
        query.add_param(str(number_tax))
        query.add_param(number_item)
        query.add_param(str(number_departament))
        query.add_param("").add_param("")
        query.add_param("%0.3f" % discount_total)
        query.add_param(str(payment_type.value))
        query.add_param(str(subject_matter.value))
        # Насколько я понял нужны только для расчетов ЮР лиц
        if code_country:
            query.add_param(code_country)
        if number_customs:
            query.add_param(number_customs)
        if excise_total:
            query.add_param(excise_total)
        self.send(query)

    def doc_subtotal(self):
        """
        Эта команда печатает промежуточный итог в чеке.

        После повторной команды «Подытог», документ переходит в состояние оплаты. Далее мы можем распечатать
        дополнительные реквизиты, прервать оформление чека командами «Отложить чек» и «Аннулировать чек»,
        либо продолжить оформление документа, выполнив команду «Оплата» и команду «Завершить документ».
        """
        self.send_command(0x44)

    # TODO Скидка на чек (0x45)

    def doc_payment(self, code_payment: int, total: float, text: str = ""):
        """
        С помощью этой команды производится фиксирование всех взаиморасчетов с клиентом с указанием сумм и типов оплаты.
        При первом использовании этой команды в чеке печатается «Итоговая сумма», что является окончательной суммой
        чека.

         При передаче суммы наличными, больше требуемой, ККТ самостоятельно рассчитывает сдачу. Сумма по безналичным
        типам платежа (с кодами от 1 до 15), не должна превышать итоговой суммы по чеку.

        Код типа платежа должен соответствовать одному из запрограммированных средств оплаты в “Таблице настроек ККТ”.
        :param code_payment: код типа платежа (0..15) из настроек кассы обычно 0 - наличными, 1-электронными
        :param total: сумма, принятая от покупателя по данному платежу
        :param text: дополнительный текст (пока не знаю зачем)
        """
        if code_payment < 0 or code_payment > 15:
            raise Exception("Неверный код типа платежа!")
        self.send(Output(0x47).add_param(str(code_payment)).add_param("%0.3f" % total).add_param(text))

    # TODO Внесение / изъятие суммы (0x48)

    @property
    def exchange_fn(self):
        """
        Функция позволяет обмениваться информацией с ФН
        :return:˚
        """
        return ExchangeFNData(self)

    def sound(self, duration: int):
        """
        Команда подает звуковой сигнал заданной длительности
        :param duration: длительность в мс (10..2000)
        """
        if duration < 10 or duration > 2000:
            raise Exception("Неверное значение длительности сигнала")
        self.send(Output(0x82).add_param(duration))


class Info:

    def __init__(self, machine: KKT):
        self.__machine = machine

    def get_manufacture_number(self):
        """
        Возвращает заводской номер
        :return: строка с заводским номером
        """
        return self.__machine.send(Output(0x02).add_param(0x31)).to_string(1)

    def get_inn(self):
        """
        Возвращает ИНН организации
        :return: строка с номером ИНН
        """
        return self.__machine.send(Output(0x02).add_param(0x33)).to_string(1)

    def __str__(self):
        return "Заводской номер: %s\n" \
               "ИНН: %s" % (self.get_manufacture_number(), self.get_inn())
