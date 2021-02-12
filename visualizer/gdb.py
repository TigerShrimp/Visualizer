from subprocess import PIPE, Popen
from queue import Empty, Queue
from threading import Thread


class GDB():
    """
    Class to handle the applications controll of GDB (https://www.gnu.org/software/gdb/)
    Handles staring of GDB as a subprocess, setting up pipes for communication and takes
    care of reading and writing to GDB.
    """

    def __init__(self):
        pass

    def read(self):
        """
        Returns:
          The contents written by the GDB to stdout since last read
        """
        lines = ""
        while True:
            line = self.reader.readline()
            lines += line
            if "(gdb)" in line and self.reader.empty():
                return lines

    def write(self, command):
        """ Writes to stdin of the GDB process and flushes the write buffer.

        Args:
          command: string command to write to GDB
        """
        encodedCommand = command.encode('Utf8')
        self.gdb_process.stdin.write(encodedCommand)
        self.gdb_process.stdin.flush()

    def start(self):
        """
        Starts the GDB subprocess and listens to its output to determine wether it started
        up without issues. If issues occurs with gdb, it will be restared until issues not
        occur. (Runs gdb ../TracingJITCompiler/build/TigerShrimp -x commands.txt -q --interpreter=mi)
        """
        cmd = ["gdb", "../TracingJITCompiler/build/TigerShrimp",
               "-x", "visualizer/commands.txt", "-q", "--interpreter=mi"]
        self.gdb_process = Popen(cmd, stdout=PIPE, stdin=PIPE)
        self.reader = Reader(self.gdb_process)
        if self.check_startup():
            return
        else:
            self.restart()

    def check_startup(self):
        while True:
            try:
                line = self.reader.readline(timeout=1)
            except Empty:
                return False
            else:
                if "(gdb)" in line and self.reader.empty():
                    return True

    def stop(self, force=False):
        self.gdb_process.stdin.close()
        self.reader.terminate()
        if force:
            self.gdb_process.kill()
        else:
            self.gdb_process.wait()

    def restart(self):
        self.stop(force=True)
        self.start()


class Reader():
    """ Class to handle asynchronous reading of stdout of the GDb process
    """

    def __init__(self, gdb_process):
        """ Sets up and starts the reader thread
            Args:
              gdg_process:
                The GDB process which stdout is to be read.
        """
        self.terminated = False
        self.read_queue = Queue()
        self.gdb_process = gdb_process
        reader = Thread(target=self.reader)
        reader.daemon = True
        reader.start()

    def readline(self, timeout=None):
        """
        Args:
          timeout: 
            If timeout is set, readline only blocks the given value (seconds)
        Returns:
          Oldest read line from the GDB process
        """
        return self.read_queue.get(timeout=timeout) if timeout else self.read_queue.get()

    def empty(self):
        return self.read_queue.empty()

    def terminate(self):
        """ Flags the thread that it should terminate. There is no guarantee on when the 
        thread terminates
        """
        self.terminated = True

    def reader(self):
        for line in iter(self.gdb_process.stdout.readline, b''):
            self.read_queue.put(line.decode('Utf8'))
            if self.terminated:
                break
