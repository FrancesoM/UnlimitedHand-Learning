#include "init_.h"

/* Following the guide at:
http://www.codeguru.com/cpp/i-n/network/serialcommunications/article.php/c5425/Serial-Communication-in-Windows.htm
*/

int init_serial_port(char* port_name,
                      HANDLE& port_handler)
{
    int dwBaudRate = CBR_115200;
    int byByteSize = 8;
    int byParity = NOPARITY;
    int byStopBits = 1;

    // port name: "\\\\.\\COM10"
    port_handler = CreateFile( port_name,
       GENERIC_READ|GENERIC_WRITE,  // access ( read and write)
       0,                           // (share) 0:cannot share the
                                    // COM port
       0,                           // security  (None)
       OPEN_EXISTING,               // creation : open_existing
       0,        // we want overlapped operation
       0                            // no templates file for
                                    // COM port...
       );

    if (port_handler == INVALID_HANDLE_VALUE)
   {
       //  Handle the error.
       printf ("CreateFile failed with error %ld.\n", GetLastError());
       return (1);
   }

    DCB dcb = {0};
    dcb.DCBlength = sizeof(DCB);

    if(!GetCommState(port_handler,&dcb)){
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


    if (!SetCommState (port_handler,&dcb))
    {
      //ASSERT(0);
      printf( "CSerialCommHelper : Failed to Set Comm State Reason:\
        %ld",GetLastError());
      return E_FAIL;
    }

    printf( "CSerialCommHelper : Current Settings are:\nBaud Rate %ld\n\
Parity %d\nByte Size %d\nStop Bits %d\n",
           dcb.BaudRate,dcb.Parity,dcb.ByteSize,dcb.StopBits);
/*
    //Since we do not want to polling the port, we use an event driven approach.
    //The function setCommMask is similar to the interrupt mask, which makes
    //enable the wake up of the port after a certain event

    SetCommMask( m_hCommPort, EV_RXCHAR|EV_TXEMPTY);
*/
    return 0;
}


BOOL WriteAChar(char* ch, HANDLE& hComm, DWORD* errors, COMSTAT* status)
{
   DWORD bytesSend;
   DWORD err;

   if(!WriteFile(hComm, (void*)ch, 1, &bytesSend, NULL))
   {
    ClearCommError(hComm,errors,status);
    err = *errors;
    if(err & CE_BREAK) printf("Error CE_BREAK");
    if(err & CE_FRAME) printf("Error CE_FRAME");
    if(err & CE_OVERRUN) printf("Error CE_OVERRUN");
    if(err & CE_RXOVER) printf("Error CE_RXOVER");
    if(err & CE_RXPARITY) printf("Error CE_RXPARITY");

    return false;
   }
   else
    return true;
}
