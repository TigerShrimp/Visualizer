#include <stdio.h>
#include <unistd.h>

#include <iostream>
#include <string>
const size_t bufferLength = 10000;
const size_t sleepLenght = 1;

void read(int* fd) {
  char buf[bufferLength];
  ssize_t res = read(fd[0], buf, bufferLength);
  if (res == -1) {
    perror("Read error");
  }
  std::string resString = std::string(buf, buf + res);
  std::cout << "Read from gdb: " << res << "\n\t" << resString << std::endl;
  sleep(sleepLenght);
}

void write(int* fd, std::string command) {
  std::cout << "Writing: " << command << std::endl;
  write(fd[1], command.c_str(), command.length() + 1);
  sleep(sleepLenght);
}
int main() {
  int stdinFD[2];
  int stdoutFD[2];

  pipe(stdinFD);
  pipe(stdoutFD);

  pid_t pid = fork();
  if (pid == 0) {  // Child process:
    // Start gdb with tigershrimp using excep
    dup2(stdoutFD[1], STDOUT_FILENO);
    close(stdoutFD[0]);
    dup2(stdinFD[0], STDIN_FILENO);
    close(stdinFD[1]);
    char* arg[6];
    arg[0] = "gdb";
    arg[1] =
        "/Users/jakoberlandsson/Documents/MasterThesis/TracingJITCompiler/"
        "build/"
        "TigerShrimp\0";
    arg[2] = "-x\0";
    arg[3] = "commands.txt\0";
    arg[4] = "-q\0";
    arg[5] = NULL;
    execvp(arg[0], arg);
    perror("execvp() failed");
    perror("Execvp error");
  } else if (pid > 0) {  // Parent process:
    close(stdoutFD[1]);
    close(stdinFD[0]);
    sleep(sleepLenght);
    read(stdoutFD);
    for (int i = 0; i < 10; i++) {
      write(stdinFD, "next\n\0");
      read(stdoutFD);
    }
    write(stdinFD, "quit\n\0");
    wait(NULL);
  } else {
    perror("Fork error");
  }
}