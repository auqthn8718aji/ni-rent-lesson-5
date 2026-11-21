from src.models import Apartment, ApartmentSettlement, Bill, Parameters, Tenant, TenantSettlement, Transfer


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key: str, year: int | None = None, month: int | None = None,) -> float | None:
        if month is not None:
            if year is None:
                raise ValueError("Month cannot be given without a year")
            if not isinstance(month, int) or not 1 <= month <= 12:
                raise ValueError(f"Invalid month: {month}")

        if apartment_key not in self.apartments:
            return None

        total = 0.0
        for bill in self.bills:
            if bill.apartment != apartment_key:
                continue
            if year is not None and bill.settlement_year != year:
                continue
            if month is not None and bill.settlement_month != month:
                continue
            total += bill.amount_pln
        return total

    def create_apartment_settlement(self, apartment_key: str, year: int, month: int) -> ApartmentSettlement | None:
        if year is None or month is None:
            raise ValueError("Both year and month are required")

        total_bills = self.get_apartment_costs(apartment_key, year, month)
        if total_bills is None:
            return None

        total_rent = 0.0
        return ApartmentSettlement(
            apartment=apartment_key,
            year=year,
            month=month,
            total_rent_pln=total_rent,
            total_bills_pln=total_bills,
            total_due_pln=total_rent - total_bills,
        )

    def create_tenant_settlements(self, apartment_settlement: ApartmentSettlement) -> list[TenantSettlement]:
        period = f"{apartment_settlement.year}-{apartment_settlement.month:02d}"
        current_tenants = [
            key
            for key, tenant in self.tenants.items()
            if tenant.apartment == apartment_settlement.apartment
            and tenant.date_agreement_from[:7] <= period <= tenant.date_agreement_to[:7]
        ]
        if not current_tenants:
            return []

        share = apartment_settlement.total_bills_pln / len(current_tenants)
        return [
            TenantSettlement(
                tenant=key,
                apartment_settlement=apartment_settlement.apartment,
                month=apartment_settlement.month,
                year=apartment_settlement.year,
                rent_pln=0.0,
                bills_pln=share,
                total_due_pln=-share,
                balance_pln=-share,
            )
            for key in current_tenants
        ]
