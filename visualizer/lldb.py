from constants import CMD_FILE_PATH
from subprocess import PIPE, Popen
from queue import Empty, Queue
from threading import Thread


class LLDB():
    """
    Class to handle the applications controll of LLDB (https://lldb.llvm.org)
    Handles staring of LLDB as a subprocess, setting up pipes for communication and takes
    care of reading and writing to LLDB.
    """

    def __init__(self):
        pass

    def read(self):
        """
        Returns:
          The contents written by the lldb to stdout since last read
        """
        lines = ""
        while True:
            line = self.reader.readline()
            lines += line
            if "(lldb)" in lines[:-3] and self.reader.empty():
                return lines

    def write(self, command):
        """ Writes to stdin of the lldb process and flushes the write buffer.

        Args:
          command: string command to write to lldb
        """
        encodedCommand = command.encode('Utf8')
        self.lldb_process.stdin.write(encodedCommand)
        self.lldb_process.stdin.flush()

    def start(self):
        """
        Starts the lldb subprocess and listens to its output to determine wether it started
        up without issues. If issues occurs with lldb, it will be restared until issues not
        occur. (Runs lldb ../TracingJITCompiler/build/TigerShrimp -x "visualizer/commands.txt" -q --interpreter=mi)
        """
        cmd = ["lldb", "../TracingJITCompiler/build/TigerShrimp",
               "--source", CMD_FILE_PATH]
        self.lldb_process = Popen(cmd, stdout=PIPE, stdin=PIPE)
        self.reader = Reader(self.lldb_process)

    def check_startup(self):
        while True:
            try:
                line = self.reader.readline(timeout=1)
            except Empty:
                return False
            else:
                if "(lldb)" in line and self.reader.empty():
                    return True

    def stop(self, force=False):
        self.lldb_process.stdin.close()
        self.reader.terminate()
        if force:
            self.lldb_process.kill()
        else:
            self.lldb_process.wait()

    def restart(self):
        self.stop(force=True)
        self.start()


class Reader():
    """ Class to handle asynchronous reading of stdout of the LLDB process
    """

    def __init__(self, lldb_process):
        """ Sets up and starts the reader thread
            Args:
              lldb_process:
                The LLDB process which stdout is to be read.
        """
        self.terminated = False
        self.read_queue = Queue()
        self.lldb_process = lldb_process
        reader = Thread(target=self.reader)
        reader.daemon = True
        reader.start()

    def readline(self, timeout=None):
        """
        Args:
          timeout: 
            If timeout is set, readline only blocks the given value (seconds)
        Returns:
          Oldest read line from the lldb process
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
        for line in iter(self.lldb_process.stdout.readline, b''):
            self.read_queue.put(line.decode('Utf8'))
            if self.terminated:
                break
