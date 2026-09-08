from datetime import date
from decimal import Decimal

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from apps.domain_validation import derive_sale_revenue, derive_sales_revenue
from apps.herds.models import Herd

from .models import SaleRecord


class SaleRecordApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="sales-manager",
            password="secretpass123",
        )
        cls.user.groups.add(Group.objects.get(name="quản lý"))
        cls.herd = Herd.objects.create(
            code="HERD-SALE-001",
            name="Sales herd",
            animal_type="cattle",
            management_mode="group",
            quantity=20,
            status="active",
        )
        cls.record = SaleRecord.objects.create(
            target=cls.herd,
            sale_date=date(2026, 9, 15),
            quantity=Decimal("12.00"),
            weight=Decimal("540.50"),
            amount=Decimal("2400.00"),
            notes="Initial sale",
        )

    def valid_payload(self, **overrides):
        payload = {
            "target": self.herd.pk,
            "sale_date": "2026-09-16",
            "quantity": "5.00",
            "weight": "250.00",
            "amount": "1200.00",
            "notes": "Valid sale",
        }
        payload.update(overrides)
        return payload

    def test_sale_api_001_unauthenticated_access_is_denied(self):
        response = self.client.get(reverse("salerecord-list"))
        self.assertIn(response.status_code, (401, 403))

    def test_sale_api_002_authenticated_list_succeeds(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("salerecord-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) >= 1)

    def test_sale_api_003_retrieve_existing_record(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("salerecord-detail", args=[self.record.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["amount"], "2400.00")

    def test_sale_api_004_valid_create(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("salerecord-list"),
            self.valid_payload(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(SaleRecord.objects.filter(amount=Decimal("1200.00")).exists())

    def test_sale_api_005_invalid_herd_reference_is_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("salerecord-list"),
            self.valid_payload(target=999999),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_sale_api_006_missing_required_fields_are_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("salerecord-list"),
            {"target": self.herd.pk},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("sale_date", response.json()["field_errors"])
        self.assertIn("amount", response.json()["field_errors"])

    def test_sale_api_007_negative_amount_is_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("salerecord-list"),
            self.valid_payload(amount="-1.00"),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_sale_api_008_negative_quantity_is_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("salerecord-list"),
            self.valid_payload(quantity="-1.00"),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_sale_api_009_negative_weight_is_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("salerecord-list"),
            self.valid_payload(weight="-1.00"),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_sale_api_010_valid_update(self):
        self.client.force_login(self.user)
        response = self.client.patch(
            reverse("salerecord-detail", args=[self.record.pk]),
            {"amount": "2500.00"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.record.refresh_from_db()
        self.assertEqual(self.record.amount, Decimal("2500.00"))

    def test_sale_api_011_invalid_update_is_rejected(self):
        self.client.force_login(self.user)
        response = self.client.patch(
            reverse("salerecord-detail", args=[self.record.pk]),
            {"weight": "-1.00"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_sale_api_012_delete(self):
        self.client.force_login(self.user)
        response = self.client.delete(reverse("salerecord-detail", args=[self.record.pk]))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(SaleRecord.objects.filter(pk=self.record.pk).exists())

    def test_sale_api_013_missing_object_returns_404(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("salerecord-detail", args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_sale_api_014_revenue_is_derived_from_amount(self):
        self.assertEqual(derive_sale_revenue(self.record), Decimal("2400.00"))

    def test_sale_api_015_multiple_sales_aggregate_revenue(self):
        second_record = SaleRecord.objects.create(
            target=self.herd,
            sale_date=date(2026, 9, 16),
            amount=Decimal("100.00"),
        )
        self.assertEqual(
            derive_sales_revenue([self.record, second_record]),
            Decimal("2500.00"),
        )

    def test_sale_api_016_no_persisted_revenue_model_exists(self):
        self.assertFalse(any(model.__name__ == "RevenueRecord" for model in apps.get_models()))

    def test_sale_api_017_quantity_and_weight_remain_optional(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("salerecord-list"),
            self.valid_payload(quantity=None, weight=None),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        record = SaleRecord.objects.get(amount=Decimal("1200.00"))
        self.assertIsNone(record.quantity)
        self.assertIsNone(record.weight)
