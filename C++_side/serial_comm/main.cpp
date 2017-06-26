#include <iostream>
#include <cstdio>
#include <ctime>
#include <windows.h>
#include <assert.h>
#include <stdio.h>
#include "init_.h"


#define BYTES_INCOMING 2*8

int main()
{
    std::clock_t start;
    double duration;
    HANDLE port;

    BOOL written = 0;
    BOOL fSuccess = 1;

    char* port_name = "\\\\.\\COM10";
    //char* port_name = "COM4";
    //init_serial_port(port_name,port);

    int dwBaudRate = CBR_115200;
    int byByteSize = 8;
    int byParity = NOPARITY;
    int byStopBits = 1;

    // port name: "\\\\.\\COM10"
    port = CreateFile( port_name,
       GENERIC_READ|GENERIC_WRITE,  // access ( read and write)
       0,                           // (share) 0:cannot share the
                                    // COM port
       0,                           // security  (None)
       OPEN_EXISTING,               // creation : open_existing
       0,        // we want overlapped operation
       0                            // no templates file for
                                    // COM port...
       );

    if (port == INVALID_HANDLE_VALUE)
   {
       //  Handle the error.
       printf ("CreateFile failed with error %ld.\n", GetLastError());
       return (1);
   }

    DCB dcb = {0};
    dcb.DCBlength = sizeof(DCB);

    if(!GetCommState(port,&dcb)){
        printf( "CSerialCommHelper : Failed to Get Comm State Reason:%ld",GetLastError());
        return E_FAIL;
    }

    dcb.BaudRate  = dwBaudRate;
    dcb.ByteSize  = byByteSize;
    dcb.Parity    = byParity;
    if ( byStopBits == 1 )
      dcb.StopBits  = ONESTOPBIT;
    else if (byStopBits == 2 )
      dcb.StopBits  = TWOSTOPBITS;
    else
      dcb.StopBits  = ONE5STOPBITS;


    if (!SetCommState (port,&dcb))
    {
      //ASSERT(0);
      printf( "CSerialCommHelper : Failed to Set Comm State Reason:\
        %ld",GetLastError());
      return E_FAIL;
    }

    printf( "CSerialCommHelper : Current Settings are:\nBaud Rate %ld\n\
Parity %d\nByte Size %d\nStop Bits %d\n",
           dcb.BaudRate,dcb.Parity,dcb.ByteSize,dcb.StopBits);



    if (port != INVALID_HANDLE_VALUE)
   {
       std::cout << "\nPort succesfully initialized" << std::endl;
   }


  COMMTIMEOUTS timeouts;
    timeouts.ReadIntervalTimeout       = MAXDWORD;
    timeouts.ReadTotalTimeoutMultiplier   = 0;
    timeouts.ReadTotalTimeoutConstant     = 0;
    timeouts.WriteTotalTimeoutMultiplier  = 0;
    timeouts.WriteTotalTimeoutConstant    = 0;

    if (!SetCommTimeouts(port, &timeouts))
       // Error setting time-outs.

   //Set the events we are interested in
   fSuccess = SetCommMask(port,EV_RXCHAR|EV_RXFLAG);

   if(!fSuccess)
   {
       printf("SetCommMask failed with error %ld",GetLastError());
   }

    DWORD dwRead;
    __int8 unsigned input_char[BYTES_INCOMING];
    char to_start = 's';
    int i = 0;
    int N = 0;

    DWORD errors;
    COMSTAT status;

    start = std::clock();

    while(N<200)
    {
        written = WriteAChar(&to_start,port,&errors,&status);
        //printf("written: %d\n",written);
        if(written){
            ClearCommError(&port,&errors,&status);
                //read data until we read all the buffer
                do{
                    ReadFile(port,&input_char[i],1,&dwRead,NULL);
                    i++;
                }while(i<BYTES_INCOMING);

//                printf("Bytes Read: %d -> \n\
//                    ch0:%u\n\
//                    ch1:%u\n\
//                    ch2:%u\n\
//                    ch3:%u\n\
//                    ch4:%u\n\
//                    ch5:%u\n\
//                    ch6:%u\n\
//                    ch7:%u\n\
//                       \n",i,
//                       input_char[0]<<8 | input_char[1],
//                       input_char[2]<<8 | input_char[3],
//                       input_char[4]<<8 | input_char[5],
//                       input_char[6]<<8 | input_char[7],
//                       input_char[8]<<8 | input_char[9],
//                       input_char[10]<<8 | input_char[11],
//                       input_char[12]<<8 | input_char[13],
//                       input_char[14]<<8 | input_char[15]);
            }
//            printf("************** Total Bytes Read: %d ****************",i);
            i= 0;

        N++;
    }

    duration = ( std::clock() - start ) / (double) CLOCKS_PER_SEC;
    std::cout<<"printf: "<< duration <<'\n';

    return 0;
}
