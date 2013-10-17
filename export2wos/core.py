import unittest
import mocker
import StringIO

import os
import ftplib
import functools


def isolate_connection(func):
    functools.wraps(func)
    def isolation(self, *args, **kwargs):
        self._connect()
        _return = func(self, *args, **kwargs)

        if not self.keep_alive:
            self._disconnect()

        return _return

    return isolation


class FTPServer(object):
    def __init__(self, host, user, password, keep_alive=False):
        """
        Encapsulate some FTP functionality.

        :param host: ftp host as string
        :param user: username as string
        :param password: password as string
        :param keep_alive: (optional) if the connection should live across actions.
        """
        self.host = host
        self.user = user
        self.password = password

        self.conn = None
        self.keep_alive = keep_alive

    def __del__(self):
        self._disconnect()

    def __enter__(self):
        self.keep_alive = True
        self._connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._disconnect()

    def _connect(self):
        if self.conn is None:
            self.conn = ftplib.FTP(self.host)
            self.conn.login(user=self.user, passwd=self.password)

    def _disconnect(self):
        if self.conn:
            self.conn.quit()
            self.conn = None

    def _cwd(self, path):
        if not self.conn:
            raise RuntimeError('Need a live connection to change the cwd')
        self.conn.cwd(path)

    def cwd(self, path):
        ftp_server = FTPServer(self.host, self.user, self.password, keep_alive=True)
        ftp_server._connect()
        ftp_server._cwd(path)
        return ftp_server

    @isolate_connection
    def send(self, fp, destination):
        """
        Sends `fp` to `destination`.

        :param fp: a file object, opened in binary form.
        :param destination: the remote path where `fp` will be sent.
        """
        if 'b' not in fp.mode:
            raise ValueError('"fp" must be a file object opened in binary form')

        command = 'STOR {}'.format(destination)
        self.conn.storbinary(command, fp)

    @isolate_connection
    def retrieve(self, filepath, callback):
        """
        Retrieves `filepath` and pass its data to `callback`.
        """
        command = 'RETR {}'.format(filepath)
        self.conn.retrbinary(command, callback)


class Clerk(object):
    """
    Responsible for performing office boy tasks.
    """
    def __init__(self, ftp):
        self.ftp = ftp
        self.in_dir = 'inbound'

    def send_take_off_files(self, base_dir, remove_sent=False):
        """
        Sends all files
        """
        for fl in os.listdir(base_dir):

            if not fl.endswith('del'):
                continue

            file_path = os.path.join(base_dir, fl)

            with open(file_path, 'rb') as fp:
                dest = self.in_dir + '/' + fl
                self.ftp.send(fp, dest)

            if remove_origin:
                os.remove(file_path)

    def sync_file_from_ftp(self, path_expr, output):
        """
        Lists all files matching `path_expr` and do some pyromaniacal stuff.

        >>> with open('/tmp/reports.txt', 'wb') as fp:
        >>>     clerk.sync_from_ftp('reports/*', fp)
        """
        base, expr = path_expr.rsplit('/', 1)

        with ftp.cwd(base) as cwd:
            report_files = ftp.conn.nlst(expr)

            def callback(data):
                output.write(data)

            for report_file in report_files:
                ftp.retrieve(report_file, callback)


######
# TESTES
######
class FTPServerTests(mocker.MockerTestCase):
    """
    ftp_server = FTPServer('localhost', 'user', 'password')
    """
    def test_ftpserver_initialization(self):
        #mock_FTPServer = self.mocker.patch(FTPServer)
        #mock_FTPServer._connect()
        #self.mocker.result(None)
        #self.mocker.replay()

        ftp_server = FTPServer('localhost', 'user', 'pass')

        self.assertEqual(ftp_server.host, 'localhost')
        self.assertEqual(ftp_server.user, 'user')
        self.assertEqual(ftp_server.password, 'pass')

    def test_send_only_binary_files(self):
        mock_FTPServer = self.mocker.patch(FTPServer)
        mock_FTPServer._connect()
        self.mocker.result(None)
        self.mocker.replay()

        fp_bar = StringIO.StringIO()
        fp_bar.mode = 'r'

        ftp_server = FTPServer('localhost', 'user', 'pass')
        self.assertRaises(ValueError, lambda: ftp_server.send(fp_bar, 'inbound/bar.txt'))

    def test_send(self):
        mock_FTPServer = self.mocker.patch(FTPServer)

        mock_FTPServer._connect()
        self.mocker.result(None)

        mock_FTPServer.conn.storbinary('STOR inbound/bar.txt', mocker.ANY)
        self.mocker.result(None)
        self.mocker.replay()

        fp_bar = StringIO.StringIO()
        fp_bar.mode = 'rb'

        ftp_server = FTPServer('localhost', 'user', 'pass')
        self.assertIsNone(ftp_server.send(fp_bar, 'inbound/bar.txt'))

    def test_retrieve(self):
        mock_FTPServer = self.mocker.patch(FTPServer)

        mock_FTPServer._connect()
        self.mocker.result(None)

        mock_FTPServer.conn.retrbinary('RETR reports/blue.txt', mocker.ANY)
        self.mocker.result(None)
        self.mocker.replay()

        ftp_server = FTPServer('localhost', 'user', 'pass')
        self.assertIsNone(ftp_server.retrieve('reports/blue.txt', lambda x: x))

    def test_cwd(self):
        mock_FTPServer = self.mocker.patch(FTPServer)
        mock_FTPConn = self.mocker.mock()

        mock_FTPServer._connect()
        self.mocker.result(None)

        mock_FTPServer.conn
        self.mocker.result(mock_FTPConn)
        self.mocker.count(4)

        mock_FTPConn.cwd('reports')
        self.mocker.result(None)
        self.mocker.replay()

        ftp_server = FTPServer('localhost', 'user', 'pass')
        ftp_server._connect()

        self.assertIsNone(ftp_server._cwd('reports'))


class ClerkTests(mocker.MockerTestCase):

    def test_send_take_off_files_only_del_suffix(self):
        mock_ftp = self.mocker.mock()
        mock_listdir = self.mocker.replace('os.listdir')

        mock_listdir('/foo/bar/')
        self.mocker.result(['a', 'b'])

        self.mocker.replay()

        clerk = Clerk(mock_ftp)
        self.assertIsNone(clerk.send_take_off_files('/foo/bar/', remove_sent=False))

