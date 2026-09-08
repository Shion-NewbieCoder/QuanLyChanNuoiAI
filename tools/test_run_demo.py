"""Readiness regressions: run with python -m unittest tools.test_run_demo."""

import contextlib
import http.server
import io
import socket
import threading
import unittest
from unittest.mock import Mock, patch

from tools import run_demo as demo


class ReadinessTests(unittest.TestCase):
    def test_windows_cleanup_targets_only_owned_tree(self):
        process = Mock(pid=12345)
        process.poll.return_value = None
        with patch.object(demo.os, "name", "nt"), \
                patch.object(demo.subprocess, "run") as run:
            demo.stop_server(process)
        self.assertEqual(run.call_args.args[0], ["taskkill", "/PID", "12345", "/T", "/F"])
        process.wait.assert_called_once_with(timeout=5)

    def test_listening_socket_without_http_is_not_ready(self):
        with socket.socket() as listener:
            listener.bind((demo.HOST, 0))
            listener.listen()
            with patch.object(demo, "PORT", listener.getsockname()[1]):
                self.assertFalse(demo.wait_for_server(Mock(poll=lambda: None), 0.2))

    def test_http_status_and_dead_process(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            status = 503

            def do_GET(self):
                self.send_response(self.status)
                self.end_headers()
                self.wfile.write(b"login")

            def log_message(self, *args):
                pass

        with http.server.ThreadingHTTPServer((demo.HOST, 0), Handler) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with patch.object(demo, "PORT", server.server_port):
                    for status in (503, 404, 200, 302):
                        Handler.status = status
                        with self.subTest(status=status):
                            self.assertEqual(
                                demo.wait_for_server(Mock(poll=lambda: None), 0.2),
                                status in (200, 302),
                            )
                    self.assertFalse(demo.wait_for_server(Mock(poll=lambda: 1)))
            finally:
                server.shutdown()
                thread.join()

    def test_interrupt_during_readiness_cleans_up_without_marker(self):
        process = Mock()
        process.poll.return_value = None
        output = io.StringIO()
        with patch.object(demo, "port_is_in_use", return_value=False), \
                patch.object(demo.os, "name", "posix"), \
                patch.object(demo.subprocess, "Popen", return_value=process), \
                patch.object(demo, "wait_for_server", side_effect=KeyboardInterrupt), \
                contextlib.redirect_stdout(output):
            self.assertEqual(demo.run_server({}), 0)
        process.terminate.assert_called_once()
        process.wait.assert_called_once_with(timeout=5)
        self.assertNotIn("[DEMO_READY]", output.getvalue())


if __name__ == "__main__":
    unittest.main()
