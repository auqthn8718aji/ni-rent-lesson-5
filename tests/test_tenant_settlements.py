import pytest
from src.manager import Manager
from src.models import Bill, Parameters, TenantSettlement


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
    ]
    return manager


def test_bills_split_equally_between_three_tenants(manager):
    apartment_settlement = manager.create_apartment_settlement('apart-polanka', 2024, 3)
    settlements = manager.create_tenant_settlements(apartment_settlement)

    assert len(settlements) == 3
    assert all(isinstance(s, TenantSettlement) for s in settlements)
    assert {s.tenant for s in settlements} == {'tenant-1', 'tenant-2', 'tenant-3'}
    for s in settlements:
        assert s.bills_pln == pytest.approx(150.0)
        assert s.total_due_pln == pytest.approx(-150.0)
        assert s.month == 3
        assert s.year == 2024
        assert s.apartment_settlement == 'apart-polanka'


def test_bills_split_between_two_tenants(manager):
    del manager.tenants['tenant-3']
    apartment_settlement = manager.create_apartment_settlement('apart-polanka', 2024, 3)
    settlements = manager.create_tenant_settlements(apartment_settlement)

    assert len(settlements) == 2
    assert [s.bills_pln for s in settlements] == [225.0, 225.0]


def test_single_tenant_pays_all_bills(manager):
    del manager.tenants['tenant-2']
    del manager.tenants['tenant-3']
    apartment_settlement = manager.create_apartment_settlement('apart-polanka', 2024, 3)
    settlements = manager.create_tenant_settlements(apartment_settlement)

    assert len(settlements) == 1
    assert settlements[0].tenant == 'tenant-1'
    assert settlements[0].bills_pln == 450.0
    assert settlements[0].total_due_pln == -450.0


def test_no_tenants_means_no_tenant_settlements(manager):
    manager.tenants = {}
    apartment_settlement = manager.create_apartment_settlement('apart-polanka', 2024, 3)

    assert manager.create_tenant_settlements(apartment_settlement) == []


def test_only_tenants_with_active_agreement_are_settled(manager):
    apartment_settlement = manager.create_apartment_settlement('apart-polanka', 2025, 1)
    assert manager.create_tenant_settlements(apartment_settlement) == []

    manager.tenants['tenant-3'].date_agreement_to = '2024-02-29'
    apartment_settlement = manager.create_apartment_settlement('apart-polanka', 2024, 3)
    settlements = manager.create_tenant_settlements(apartment_settlement)
    assert {s.tenant for s in settlements} == {'tenant-1', 'tenant-2'}
