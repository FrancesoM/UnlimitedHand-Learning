#ifndef SERIALHANDLER_H
#define SERIALHANDLER_H

#include "windows.h"
#include "stdio.h"
#include <queue>


#define BYTES_INCOMING 16
#define SUCCESS 1

#define START_FRAME 0b00000111

#define PUSH_BUF(buf)  buf.push( input_buffer[0]<<8 | input_buffer[1]);\
                       buf.push( input_buffer[2]<<8 | input_buffer[3]);\
                       buf.push( input_buffer[4]<<8 | input_buffer[5]);\
                       buf.push( input_buffer[6]<<8 | input_buffer[7]);\
                       buf.push( input_buffer[8]<<8 | input_buffer[9]);\
                       buf.push( input_buffer[10]<<8 | input_buffer[11]);\
                       buf.push( input_buffer[12]<<8 | input_buffer[13]);\
                       buf.push( input_buffer[14]<<8 | input_buffer[15]);

#define CHECK_ERROR     err = this->errors;\
                        if(err & CE_BREAK) printf("Error CE_BREAK");\
                        if(err & CE_FRAME) printf("Error CE_FRAME");\
                        if(err & CE_OVERRUN) printf("Error CE_OVERRUN");\
                        if(err & CE_RXOVER) printf("Error CE_RXOVER");\
                        if(err & CE_RXPARITY) printf("Error CE_RXPARITY");

#define DISPLAY_     printf("Bytes Read: %d -> \n\
            ch0:%u\n\
            ch1:%u\n\
            ch2:%u\n\
            ch3:%u\n\
            ch4:%u\n\
            ch5:%u\n\
            ch6:%u\n\
            ch7:%u\n\
               \n",i,\
               input_buffer[0]<<8 | input_buffer[1],\
               input_buffer[2]<<8 | input_buffer[3],\
               input_buffer[4]<<8 | input_buffer[5],\
               input_buffer[6]<<8 | input_buffer[7],\
               input_buffer[8]<<8 | input_buffer[9],\
               input_buffer[10]<<8 | input_buffer[11],\
               input_buffer[12]<<8 | input_buffer[13],\
               input_buffer[14]<<8 | input_buffer[15]);

class SerialHandler
{
    public:
        SerialHandler(char* port_name,
                      int baud,
                      int stop_bits,
                      int parity,
                      int frame_size);
        virtual ~SerialHandler();

        //This function does the initialization work, and set baudrate and other
        //options for the serial comm.
        BOOL init_serial_port();

        //Initialize the timeouts
        BOOL init_timeouts();

        //This function does the writing of a character to a port
        BOOL WriteAChar(__int8 unsigned* char_to_send);

        //This function reads a char from the port
        BOOL ReadAChar_PutInBuffer();

        BOOL Read_FSM(std::queue<__int16 unsigned> &input_queue);

        BOOL FlushBuffer();

    protected:

    private:
        //Variables for serial configuration
        char* port_name;
        HANDLE port_handler;
        DWORD dwBaudRate;
        BYTE byByteSize;
        BYTE byParity;
        BYTE byStopBits;
        DCB dcb;

        COMMTIMEOUTS timeouts;
        COMSTAT status;

        DWORD errors;

        //Buffer that stores the data after a read has been completed
        __int8 unsigned input_buffer[BYTES_INCOMING];
        DWORD bytesRead;


};

#endif // SERIALHANDLER_H
