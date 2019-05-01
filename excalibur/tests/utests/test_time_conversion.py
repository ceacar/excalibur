import unittest
import excalibur
import datetime


class TestTimeConversion(unittest.TestCase):
    def test_convert_timestamp_between_timezones(self):
        dt_obj = datetime.datetime(2019, 5, 1, 18, 20, 28)
        dt_obj_converted = excalibur.convert_timestamp_between_timezones(
            dt_obj,
            excalibur.get_utc_timezone_name(),
            excalibur.get_ny_timezone_name()
        )
        expected_dt_obj = datetime.datetime(2019, 5, 1, 14, 20, 28)
        # expected_dt_obj = excalibur.set_datetime_obj_timezone(expected_dt_obj, excalibur.get_ny_timezone_name())
        self.assertEqual(dt_obj_converted.replace(tzinfo=None), expected_dt_obj)
