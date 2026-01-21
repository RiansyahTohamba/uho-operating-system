<!-- setup -->
sudo apt update
sudo apt install build-essential

lalu
gcc --version

<!-- intro -->
gcc hello.c -o hello
./hello

<!-- untuk pthread -->
gcc thread.c -o thread -pthread


