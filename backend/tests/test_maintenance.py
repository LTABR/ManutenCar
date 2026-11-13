import unittest
from datetime import date, timedelta

from app.maintenance import calculate_maintenance
from app.models import Part, part_payload
from app.schemas import PartResponse


class CalculateMaintenanceTests(unittest.TestCase):
    def test_mileage_limit_expires_before_calendar_limit(self):
        estimate = calculate_maintenance(
            "engine-oil", date(2025, 1, 1), weekly_usage_km=1_000
        )

        self.assertEqual(estimate.due_by, "mileage")
        self.assertEqual(estimate.mileage_due, date(2025, 3, 12))
        self.assertEqual(estimate.expires_at, estimate.mileage_due)

    def test_calendar_limit_expires_when_mileage_is_low(self):
        estimate = calculate_maintenance(
            "engine-oil", date(2025, 1, 1), weekly_usage_km=100
        )

        self.assertEqual(estimate.due_by, "time")
        self.assertEqual(estimate.expires_at, date(2026, 1, 1))

    def test_wear_uses_the_more_advanced_limit_and_caps_at_expiry(self):
        estimate = calculate_maintenance(
            "engine-oil",
            date(2025, 1, 1),
            weekly_usage_km=100,
            as_of=date(2025, 7, 2),
        )

        self.assertEqual(estimate.wear_percent, 49.9)
        expired = calculate_maintenance(
            "engine-oil",
            date(2025, 1, 1),
            weekly_usage_km=100,
            as_of=date(2027, 1, 1),
        )
        self.assertEqual(expired.wear_percent, 100)

    def test_logging_maintenance_resets_wear_and_expiry(self):
        estimate = calculate_maintenance(
            "engine-oil",
            date(2025, 1, 1),
            weekly_usage_km=500,
            as_of=date(2025, 6, 1),
        )
        renewed = calculate_maintenance(
            "engine-oil",
            date(2025, 6, 1),
            weekly_usage_km=500,
            as_of=date(2025, 6, 1),
        )

        self.assertGreater(estimate.wear_percent, 0)
        self.assertEqual(renewed.wear_percent, 0)
        self.assertEqual(renewed.expires_at, date(2025, 10, 19))

    def test_calendar_expiry_handles_leap_day(self):
        estimate = calculate_maintenance(
            "engine-oil", date(2024, 2, 29), weekly_usage_km=0
        )

        self.assertEqual(estimate.calendar_due, date(2025, 2, 28))
        self.assertEqual(estimate.expires_at, date(2025, 2, 28))

    def test_part_response_includes_calculated_fields(self):
        part = Part(
            id="part-1",
            part_type_id="engine-oil",
            last_maintenance=date.today(),
        )

        response = PartResponse.model_validate(part_payload(part, 500))

        self.assertEqual(response.expiresAt, date.today() + timedelta(days=140))
        self.assertEqual(response.wearPercent, 0)
        self.assertEqual(response.dueBy, "mileage")


if __name__ == "__main__":
    unittest.main()
