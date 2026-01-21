<!-- setup -->
sudo apt update
sudo apt install build-essential

lalu
gcc --version

<!-- intro -->
gcc intro.c -o ./out/intro
./out/intro

<!-- untuk pthread -->
gcc thread.c -o thread -pthread


child_process.c