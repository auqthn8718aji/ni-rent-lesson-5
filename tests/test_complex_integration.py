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
    assert manager.get_apartment_costs('invalid-key', 2024, 3) is None
    assert manager.get_apartment_costs('invalid-key', 2024) is None
    assert manager.get_apartment_costs('invalid-key') is None


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


def test_whole_year_when_month_is_missing(manager):
    assert manager.get_apartment_costs('apart-polanka', 2024) == 450.0 + 999.0
    assert manager.get_apartment_costs('apart-polanka', 2023) == 888.0
    assert manager.get_apartment_costs('apart-polanka', 2021) == 0.0


def test_whole_history_when_year_is_missing(manager):
    assert manager.get_apartment_costs('apart-polanka') == 450.0 + 999.0 + 888.0


@pytest.mark.parametrize('month', [0, 13, -1, 100])
def test_invalid_month_raises(manager, month):
    with pytest.raises(ValueError):
        manager.get_apartment_costs('apart-polanka', 2024, month)


def test_month_without_year_raises(manager):
    with pytest.raises(ValueError):
        manager.get_apartment_costs('apart-polanka', month=3)


def test_invalid_month_is_checked_even_for_unknown_apartment(manager):
    with pytest.raises(ValueError):
        manager.get_apartment_costs('invalid-key', 2024, 13)


def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0
