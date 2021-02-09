#include <stdio.h>
#include <unistd.h>

#include <iostream>
#include <string>

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
    char* arg[3];
    arg[0] = "gdb";
    arg[1] =
        "/Users/skarrman/Projects/Thesis/TigerShrimp/TracingJITCompiler/build/"
        "TigerShrimp\0";
    arg[2] = NULL;
    execvp(arg[0], arg);
    perror("execvp() failed");
    perror("Execvp error");
  } else if (pid > 0) {  // Parent process:
    close(stdoutFD[1]);
    close(stdinFD[0]);
    sleep(1);
    char buf[1000];
    read(stdoutFD[0], buf, 1000);
    std::cout << "Read from gdb:\n\t" << buf << std::endl;
    char* run =
        "run "
        "/Users/skarrman/Projects/Thesis/TigerShrimp/TracingJITCompiler/test/"
        "main.java\n\0";
    write(stdinFD[1], run, strlen(run) + 1);
    sleep(5);
    char buf1[1000];
    read(stdoutFD[0], buf1, 1000);
    std::cout << "Read from gdb:\n\t" << buf1 << std::endl
              << "-- End ---" << std::endl;

    wait(NULL);
  } else {
    perror("Fork error");
  }
}