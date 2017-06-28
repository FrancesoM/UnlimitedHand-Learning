#include <iostream>
#include <cstdio>
#include <ctime>
#include <stdio.h>
#include "SerialHandler.h"
#include <queue>
#include <condition_variable>
#include <fstream>

#include <thread>
#include <mutex>


std::mutex mut;
std::queue<__int16 unsigned> input_data_queue;
std::condition_variable data_cond;

bool flag_time_elapsed = 0;

/*

    Documentation in "readme.md"

*/

void read_data_thread(double ms_time)
{
    //For COM > 9 USE \\\\.\\COM10

    SerialHandler _S("\\\\.\\COM10",
                     115200,
                     1,
                     0,
                     8);

    _S.init_serial_port();
    _S.init_timeouts();

    char s = 's';
    std::clock_t start;
    double duration;

    while(!_S.WriteAChar(&s)); //starts communication


    start = std::clock();
    while(!flag_time_elapsed)
    {
    std::lock_guard<std::mutex> lk(mut); //lk is the lock guard

    if(_S.Read_FSM(input_data_queue))  //if read succeded
    {
        data_cond.notify_one();
    }

    duration = ( std::clock() - start ) / (double) CLOCKS_PER_SEC;

    if (duration > ms_time){
        flag_time_elapsed = true;
        std::cout<< "Elapsed: " << duration << '\n';
    }

    }
}

void process_data_thread(char* namefile){

    std::ofstream record;
    record.open(namefile);

    while(!flag_time_elapsed){
        std::unique_lock<std::mutex> lk(mut);
        data_cond.wait(
                       lk, []{return !input_data_queue.empty();});
    int upper_limit = input_data_queue.size();
    for(int i = 0;i<upper_limit;i++)
    {
        //std::cout << input_data_queue.front() << std::endl;
        record << input_data_queue.front() << ',';
        input_data_queue.pop();
    }

    record << 'x' << std::endl; //x will be the type of movement.

    lk.unlock();

    }

    record.close();

}

int main(int argc, char** argv)
{
    double ms_time;
    char* namefile;
    for(int arg = 0;arg<argc;arg++)
    {
        char* new_arg = argv[arg];
        char identifier = new_arg[1];
        switch(identifier)
            {
            case 't':
                ms_time = static_cast<double> (atoi(argv[arg+1]) );
                ms_time = ms_time/1000;
            case 'n':
                namefile = argv[arg+1];
            default:
                ms_time = 1;
                namefile = "default.txt";

            }
    }

    std::cout << "Starting Counting: " << ms_time << '\n';

    std::thread read(read_data_thread,ms_time);
    std::thread process(process_data_thread,namefile);


    read.join();
    process.join();

    return 0;
}
