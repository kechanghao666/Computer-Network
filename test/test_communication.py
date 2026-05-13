import socketserver
import tempfile
import threading
import unittest
from pathlib import Path

from client.communication import (
    AtmCommunication,
    CommunicationError,
    format_amount,
    parse_response,
)


class FakeAtmHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.logged_in = False
        self.username = None

        while True:
            raw = self.rfile.readline()
            if not raw:
                break

            request = raw.decode("utf-8").strip()
            command, _, data = request.partition(" ")

            if command == "HELO":
                if data == "zhangsan":
                    self.username = data
                    self._write("200 OK Username accepted")
                else:
                    self._write("401 ERROR User not found")
            elif command == "PASS":
                if self.username == "zhangsan" and data == "123456":
                    self.logged_in = True
                    self._write("200 OK Login success")
                else:
                    self._write("400 ERROR Wrong password")
            elif command == "BALA":
                self._write("201 OK Balance: 5000.00 RMB")
            elif command == "WITHDRAW":
                self._write("202 OK Withdraw success, Balance: 4500.00 RMB")
            elif command == "DEPOSIT":
                self._write("203 OK Deposit success, Balance: 5300.00 RMB")
            elif command == "FLOW":
                self._write("204 OK Flow query success")
            elif command == "PING":
                self._write("PONG")
            elif command == "QUIT":
                self._write("300 OK Quit success")
                break
            else:
                self._write("500 ERROR Invalid command")

    def _write(self, response):
        self.wfile.write(f"{response}\n".encode("utf-8"))


class ThreadedTcpServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


class CommunicationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadedTcpServer(("127.0.0.1", 0), FakeAtmHandler)
        cls.host, cls.port = cls.server.server_address
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def setUp(self):
        self.client = AtmCommunication(self.host, self.port, timeout=1, record_rtt=False)
        self.client.connect_server()

    def tearDown(self):
        self.client.close_connection()

    def test_parse_response(self):
        response = parse_response("201 OK Balance: 5000.00 RMB")
        self.assertTrue(response.is_success)
        self.assertEqual(response.code, 201)
        self.assertEqual(response.phrase, "OK")
        self.assertEqual(response.message, "Balance: 5000.00 RMB")

    def test_format_amount(self):
        self.assertEqual(format_amount("500"), "500.00")
        self.assertEqual(format_amount(12.345), "12.35")
        self.assertIsNone(format_amount("abc"))
        self.assertIsNone(format_amount("-1"))

    def test_login_and_business_requests(self):
        login_response = self.client.login("zhangsan", "123456")
        self.assertEqual(login_response.code, 200)
        self.assertTrue(login_response.is_success)

        balance_response = self.client.query_balance()
        self.assertEqual(balance_response.code, 201)

        withdraw_response = self.client.withdraw(500)
        self.assertEqual(withdraw_response.code, 202)

        deposit_response = self.client.deposit("300")
        self.assertEqual(deposit_response.code, 203)

        flow_response = self.client.query_flow()
        self.assertEqual(flow_response.code, 204)

    def test_login_user_not_found(self):
        response = self.client.login("unknown", "123456")
        self.assertEqual(response.code, 401)
        self.assertTrue(response.is_error)

    def test_local_invalid_amount(self):
        response = self.client.withdraw("bad")
        self.assertEqual(response.code, 403)
        self.assertTrue(response.is_error)

    def test_rtt(self):
        result = self.client.test_rtt(count=5)
        self.assertTrue(result.success)
        self.assertEqual(result.count, 5)
        self.assertEqual(len(result.values), 5)
        self.assertIsNotNone(result.min_ms)
        self.assertIsNotNone(result.max_ms)
        self.assertIsNotNone(result.avg_ms)

    def test_rtt_persists_record_when_enabled(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "atm.db"
            client = AtmCommunication(
                self.host,
                self.port,
                timeout=1,
                record_rtt=True,
                rtt_db_path=str(db_path),
            )
            client.connect_server()
            try:
                result = client.test_rtt(count=5)
            finally:
                client.close_connection()

            self.assertTrue(result.success)
            self.assertIsNotNone(result.record_id)
            self.assertIsNone(result.record_error)

    def test_rtt_rejects_non_pong_success_response(self):
        class BadPongClient(AtmCommunication):
            def request(self, request_text):
                return parse_response("200 OK Not pong")

        result = BadPongClient(record_rtt=False).test_rtt(count=5)

        self.assertFalse(result.success)
        self.assertEqual(result.count, 0)
        self.assertEqual(result.error, "200 OK Not pong")

    def test_quit(self):
        response = self.client.quit_system()
        self.assertEqual(response.code, 300)
        self.assertFalse(self.client.is_connected)

    def test_connect_failed(self):
        bad_client = AtmCommunication("127.0.0.1", 1, timeout=0.1, record_rtt=False)
        with self.assertRaises(CommunicationError):
            bad_client.connect_server()


if __name__ == "__main__":
    unittest.main()

