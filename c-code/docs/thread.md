Berikut versi kode yang **lengkap (C, POSIX-style)**, lalu **jawaban dan penjelasan langkah demi langkah** sesuai asumsi di **Silberschatz**.

---

## Kode lengkap

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <pthread.h>

void* thread_func(void* arg) {
    return NULL;
}

int main() {
    pid_t pid;
    pthread_t tid;

    pid = fork();

    if (pid == 0) {          /* child process */
        fork();              /* create another process */
        pthread_create(&tid, NULL, thread_func, NULL);
    }

    fork();                  /* executed by all existing processes */

    return 0;
}
```

---

## a. Berapa **unique processes** yang dibuat?

**Jawaban: 6 proses**

### Penjelasan

1. **Awal**

   * 1 proses (P0)

2. **`pid = fork()`**

   * P0 → P1
   * Total: **2 proses**

3. **Blok `if (pid == 0)` hanya dijalankan oleh P1**

   * `fork()` → P1 membuat P2
   * Total: **3 proses (P0, P1, P2)**

4. **`fork()` terakhir dijalankan oleh semua proses**

   * P0 → P3
   * P1 → P4
   * P2 → P5

**Total akhir: 6 proses**

---

## b. Berapa **unique threads** yang dibuat?

**Jawaban: 8 thread**

### Aturan penting (Silberschatz / POSIX):

> Jika `fork()` dipanggil pada proses multithread, **child hanya memiliki satu thread**, yaitu thread yang memanggil `fork()`.

### Perhitungan

Sebelum `fork()` terakhir:

| Proses | Thread               |
| ------ | -------------------- |
| P0     | 1 (main)             |
| P1     | 2 (main + 1 pthread) |
| P2     | 2 (main + 1 pthread) |

Setelah `fork()` terakhir:

| Proses baru  | Thread |
| ------------ | ------ |
| P3 (dari P0) | 1      |
| P4 (dari P1) | 1      |
| P5 (dari P2) | 1      |

### Total thread

```
P0 : 1
P1 : 2
P2 : 2
P3 : 1
P4 : 1
P5 : 1
----------------
Total = 8 thread
```

---

## Ringkasan Jawaban

| Pertanyaan       | Jawaban |
| ---------------- | ------- |
| Unique processes | **6**   |
| Unique threads   | **8**   |

Jika Anda mau, saya bisa:

* menggambar **process–thread tree diagram**, atau
* membahas **variasi soal** (misalnya `vfork()` atau `exec()`) yang sering muncul di ujian OS.
