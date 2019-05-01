import unittest
import excalibur
import mock
import datetime


class TestRequestTimeUtils(unittest.TestCase):
    def mock_requests(self):
        return {
            'Content-Length': '49268393',
            'Accept-Ranges': 'bytes',
            'Server': 'lighttpd/1.4.47',
            'Last-Modified': 'Wed, 01 May 2019 18:20:28 GMT',
            'ETag': '"3003862200"',
            'Date': 'Wed, 01 May 2019 18:28:49 GMT',
            'Content-Type': 'text/plain; charset=utf-8'}

    def setUp(self):
        self.url = 'http://www.google.com'

    def test_get_file_timestamp(self):
        with mock.patch('requests.head') as moc:
            moc.return_value = self.mock_requests()
            dt_obj = excalibur.get_file_timestamp(self.url, auth={})
            expected_dt_obj = datetime.datetime(2019, 5, 1, 18, 20, 28)
            self.assertEqual(dt_obj, expected_dt_obj)
