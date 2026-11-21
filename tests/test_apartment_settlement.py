import pytest
from src.manager import Manager
from src.models import ApartmentSettlement, Bill, Parameters


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
    ]
    return manager


def test_settlement_for_apartment_with_bills(manager):
    settlement = manager.create_apartment_settlement('apart-polanka', 2024, 3)

    assert isinstance(settlement, ApartmentSettlement)
    assert settlement.apartment == 'apart-polanka'
    assert settlement.year == 2024
    assert settlement.month == 3
    assert settlement.total_bills_pln == 450.0
    assert settlement.total_rent_pln == 0.0
    assert settlement.total_due_pln == -450.0


def test_settlement_for_apartment_without_bills_in_month(manager):
    settlement = manager.create_apartment_settlement('apart-polanka', 2024, 5)

    assert settlement.apartment == 'apart-polanka'
    assert settlement.total_bills_pln == 0.0
    assert settlement.total_rent_pln == 0.0
    assert settlement.total_due_pln == 0.0


def test_settlement_ignores_other_months_and_years(manager):
    assert manager.create_apartment_settlement('apart-polanka', 2024, 4).total_bills_pln == 999.0
    assert manager.create_apartment_settlement('apart-polanka', 2023, 3).total_bills_pln == 888.0


def test_settlement_for_unknown_apartment_is_none(manager):
    assert manager.create_apartment_settlement('invalid-key', 2024, 3) is None


@pytest.mark.parametrize('year, month', [(2024, 13), (2024, 0), (None, 3), (2024, None)])
def test_settlement_requires_valid_year_and_month(manager, year, month):
    with pytest.raises(ValueError):
        manager.create_apartment_settlement('apart-polanka', year, month)
