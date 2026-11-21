import pytest

from src.manager import Manager
from src.models import Bill, Parameters


def make_bill(apartment, year, month, amount, bill_type='rent'):
    return Bill(
        amount_pln=amount,
        date_due=f'{year}-{month:02d}-15',
        apartment=apartment,
        settlement_year=year,
        settlement_month=month,
        type=bill_type,
    )


@pytest.fixture
def manager():
    manager = Manager(Parameters())
    manager.bills = [
        make_bill('apart-polanka', 2024, 3, 300.0, 'rent'),
        make_bill('apart-polanka', 2024, 3, 100.0, 'electricity'),
        make_bill('apart-polanka', 2024, 3, 50.0, 'water'),
        make_bill('apart-polanka', 2024, 4, 999.0),
        make_bill('apart-polanka', 2023, 3, 888.0),
        make_bill('apart-other', 2024, 3, 777.0),
    ]
    return manager


def test_apartment_does_not_exist(manager):
    with pytest.raises(ValueError):
        manager.get_apartment_costs('invalid-key', 2024, 3)


def test_no_bills_in_given_month(manager):
    assert manager.get_apartment_costs('apart-polanka', 2024, 5) == 0.0
    assert manager.get_apartment_costs('apart-polanka', 2022, 3) == 0.0


def test_sums_bills_for_given_month(manager):
    assert manager.get_apartment_costs('apart-polanka', 2024, 3) == 450.0
    assert manager.get_apartment_costs('apart-polanka', 2024, 4) == 999.0
    assert manager.get_apartment_costs('apart-polanka', 2023, 3) == 888.0


def test_costs_from_real_data():
    manager = Manager(Parameters())
    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 910.0
