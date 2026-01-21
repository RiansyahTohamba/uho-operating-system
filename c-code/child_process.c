#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <pthread.h>

void* thread_func(void* arg) {
    printf("[THREAD]   PID=%d, TID=%lu\n",
           getpid(), (unsigned long)pthread_self());
    return NULL;
}

int main() {
    pid_t pid;
    pthread_t tid;

    printf("[START]    PID=%d, PPID=%d\n", getpid(), getppid());

    pid = fork();

    if (pid == 0) {   /* child process */
        printf("[CHILD1]  PID=%d, PPID=%d (after first fork)\n",
               getpid(), getppid());

        fork();  /* second fork inside child */

        printf("[CHILD2]  PID=%d, PPID=%d (after second fork)\n",
               getpid(), getppid());

        pthread_create(&tid, NULL, thread_func, NULL);
        pthread_join(tid, NULL);
    }

    fork();  /* fork executed by all existing processes */

    printf("[FINAL]    PID=%d, PPID=%d\n", getpid(), getppid());

    return 0;
}
