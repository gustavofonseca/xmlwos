import unittest
import mocker
import StringIO

import os
import ftplib


class FTPServer(object):
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

        self._connect()

    def _connect(self):
        if not hasattr(self, 'conn'):
            self.conn = ftplib.FTP(self.host)
            self.conn.login(user=self.user, passwd=self.password)

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

            if fl.split('.')[-1] != 'del':
                continue

            file_path = os.path.join(base_dir, fl)

            with open(file_path, 'rb') as fp:
                dest = self.in_dir + '/' + fl
                self.ftp.send(fp, dest)

            if remove_origin:
                os.remove(file_path)


######
# TESTES
######
class FTPServerTests(mocker.MockerTestCase):
    """
    ftp_server = FTPServer('localhost', 'user', 'password')
    """
    def test_ftpserver_initialization(self):
        mock_FTPServer = self.mocker.patch(FTPServer)
        mock_FTPServer._connect()
        self.mocker.result(None)
        self.mocker.replay()

        ftp_server = FTPServer('localhost', 'user', 'pass')

        self.assertEqual(ftp_server.host, 'localhost')
        self.assertEqual(ftp_server.user, 'user')
        self.assertEqual(ftp_server.password, 'pass')

    def test_ftp_connection_on_init(self):
        mock_ftplib = self.mocker.replace('ftplib')
        mock_ftp = self.mocker.mock()

        mock_ftplib.FTP('localhost')
        self.mocker.result(mock_ftp)

        mock_ftp.login(user='user', passwd='pass')
        self.mocker.result(None)

        self.mocker.replay()

        ftp_server = FTPServer('localhost', 'user', 'pass')
        self.assertTrue(hasattr(ftp_server, 'conn'))

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


class ClerkTests(mocker.MockerTestCase):

    def test_send_take_off_files_only_del_suffix(self):
        mock_ftp = self.mocker.mock()
        mock_listdir = self.mocker.replace('os.listdir')

        mock_listdir('/foo/bar/')
        self.mocker.result(['a', 'b'])

        self.mocker.replay()

        clerk = Clerk(mock_ftp)
        self.assertIsNone(clerk.send_take_off_files('/foo/bar/', remove_sent=False))

