import atexit
import os
import sys
import time
from signal import SIGTERM


class Daemon:
    def __init__(self, pid_file,
                 stdin='/dev/null',
                 stdout='/dev/null',
                 stderr='/dev/null') -> None:
        self.pid_file = pid_file
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def start(self):
        self._guarantee_singleton()
        self._daemonize()
        self.run()

    def stop(self):
        pid = self._get_current_pid()
        if not pid:
            message = '{} not exists, Daemon not running!'.format(self.pid_file)
            sys.stderr.write(message)
            return

        self._kill_pid(pid)

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        # user implemented codes here
        while True:
            time.sleep(2)
            sys.stdout.write('{}'.format(time.ctime()))

    def _kill_pid(self, pid):
        try:
            while True:
                os.kill(pid, SIGTERM)
                time.sleep(0.5)
        except OSError as e:
            self.exit_callback()
            sys.stderr.write('kill {} error: {}'.format(pid, e))
            sys.exit(1)

    def _get_current_pid(self):
        try:
            with open(self.pid_file, 'r') as pid_file:
                pid = int(pid_file.read().strip())
        except OSError as e:
            pid = None

        return pid

    def _daemonize(self):
        self._fork_pid()
        self._setup_permission()
        self._fork_pid()
        self._redirect_file_description()
        self._setup_exit()
        self._create_pid_file()

    def _guarantee_singleton(self):
        pid = self._get_current_pid()

        if pid:
            if self._pid_exists(pid):
                message = '{} exists, Daemon already running!'.format(self.pid_file)
                sys.stderr.write(message)
                sys.exit(1)

    def _pid_exists(self, pid):
        if pid < 0: return False
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        else:
            return True

    def exit_callback(self):
        try:
            os.remove(self.pid_file)
        except OSError as e:
            sys.stderr.write('remove pid file error: {}, {}'.format(e.errno, e.strerror))

    def _create_pid_file(self):
        current_pid = str(os.getpid())
        with open(self.pid_file, 'w+') as pid_file:
            pid_file.write('{}'.format(current_pid))

    def _setup_exit(self):
        atexit.register(self.exit_callback)

    def _setup_permission(self, umask=0):
        os.chdir('/')
        os.setsid()
        os.umask(umask)

    def _redirect_file_description(self):
        sys.stdout.flush()
        sys.stderr.flush()
        redirect_stdin = open(self.stdin, 'r')
        redirect_stdout = open(self.stdout, 'a+')
        redirect_stderr = open(self.stderr, 'a+')
        os.dup2(redirect_stdin.fileno(), sys.stdin.fileno())
        os.dup2(redirect_stdout.fileno(), sys.stdout.fileno())
        os.dup2(redirect_stderr.fileno(), sys.stderr.fileno())

    def _fork_pid(self):
        try:
            child_pid = os.fork()
            if child_pid:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('fork failed: {}, {}'.format(e.errno, e.strerror))
            sys.exit(1)


if __name__ == '__main__':
    daemon = Daemon('/Users/andyguo/Desktop/test/daemon/pid.txt',
                    stdout='/Users/andyguo/Desktop/test/daemon/stdout.log')
    daemon.stop()
