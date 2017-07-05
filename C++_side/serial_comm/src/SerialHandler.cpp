#include "SerialHandler.h"

SerialHandler::SerialHandler(char* port_name,
                             int baud,
                             int stop_bits,
                             int parity,
                             int frame_size)
{
        this->port_name = port_name;

        if(baud == 115200) this->dwBaudRate = CBR_115200;
        if(baud == 9600) this->dwBaudRate = CBR_9600;
        if(stop_bits == 1) this->byStopBits = ONESTOPBIT;
        if(frame_size == 8) this->byByteSize = 8;
        if(parity == 0) this->byParity = NOPARITY;


}

SerialHandler::~SerialHandler()
{
    CloseHandle(this->port_handler);
}

BOOL SerialHandler::init_serial_port()
{
    this->port_handler = CreateFile( this->port_name,
       GENERIC_READ|GENERIC_WRITE,  // access ( read and write)
       0,                           // (share) 0:cannot share the
                                    // COM port
       0,                           // security  (None)
       OPEN_EXISTING,               // creation : open_existing
       0,        // we want overlapped operation
       0                            // no templates file for
                                    // COM port...
       );

        if (this->port_handler == INVALID_HANDLE_VALUE)
       {
           //  Handle the error.
           printf ("CreateFile failed with error %ld.\n", GetLastError());
           return (1);
       }

       this->dcb = {0};
       this->dcb.DCBlength = sizeof(DCB);

       if(!GetCommState(this->port_handler,&(this->dcb))){
        printf( "CSerialCommHelper : Failed to Get Comm State Reason:%ld",GetLastError());
        return E_FAIL;
        }

        this->dcb.BaudRate  = this->dwBaudRate;
        this->dcb.ByteSize  = this->byByteSize;
        this->dcb.Parity    = this->byParity;
        this->dcb.StopBits  = this->byStopBits;


        if (!SetCommState (this->port_handler,&(this->dcb)))
        {
          //ASSERT(0);
          printf( "CSerialCommHelper : Failed to Set Comm State Reason:\
            %ld",GetLastError());
          return E_FAIL;
        }

        printf( "CSerialCommHelper : Current Settings are:\nBaud Rate %ld\n\
    Parity %d\nByte Size %d\nStop Bits %d\n",
               this->dcb.BaudRate,this->dcb.Parity,this->dcb.ByteSize,this->dcb.StopBits);


    return SUCCESS;

}

BOOL SerialHandler::init_timeouts()
{
    this->timeouts.ReadIntervalTimeout       = MAXDWORD;
    this->timeouts.ReadTotalTimeoutMultiplier   = 0;
    this->timeouts.ReadTotalTimeoutConstant     = 0;
    this->timeouts.WriteTotalTimeoutMultiplier  = 0;
    this->timeouts.WriteTotalTimeoutConstant    = 0;

    if (!SetCommTimeouts(this->port_handler, &(this->timeouts)))
       printf("// Error setting time-outs. Error: %ld",GetLastError());
       return E_FAIL;

    return SUCCESS;
}

BOOL SerialHandler::WriteAChar(__int8 unsigned *char_to_send)
{
    DWORD bytesSend;
    DWORD err;

    if(!WriteFile(this->port_handler, (void*)char_to_send, 1, &bytesSend, NULL))
    {
        printf("Error on write: %ld",GetLastError());

        ClearCommError(this->port_handler,&(this->errors),&(this->status));
        err = this->errors;
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

BOOL SerialHandler::ReadAChar_PutInBuffer()
{
    int i = 0;
    ClearCommError(this->port_handler,&(this->errors),&(this->status));
    //read data until we read all the buffer
    do{
        ReadFile(this->port_handler,&input_buffer[i],1,&(this->bytesRead),NULL);
        i++;
    }while(i<BYTES_INCOMING);
    i = 0;

    //Formatting for the output
    DISPLAY_

//            printf("************** Total Bytes Read: %d ****************",i);

    return TRUE;

}

BOOL SerialHandler::Read_FSM(std::queue<__int16 unsigned> &input_queue){


    int internal_state=0;
    int flag = 1;
    BOOL bErrorFlag = FALSE;
    __int8 unsigned current_read;
    DWORD err;


    ClearCommError(this->port_handler,&(this->errors),&(this->status));

    //FlushFileBuffers(this->port_handler);

    CHECK_ERROR;


    do{
        bErrorFlag = ReadFile(this->port_handler,&current_read,1,&(this->bytesRead),NULL);
        //printf("Reading %ld Bytes: %02x Internal State: %d\n",this->bytesRead,current_read,internal_state);

        if(FALSE==bErrorFlag)
        {
            printf("Error: %ld",GetLastError());
        }

        if(this->bytesRead > 0){

            if(current_read == 0x21){
                internal_state++;
                //printf("Detected a !, upgrading internal state: %d\n",internal_state);
            }

            if(internal_state == 3){
                ReadFile(this->port_handler,this->input_buffer,16,&(this->bytesRead),NULL);
                //DISPLAY_
                //printf("Reading %ld bytes\n",this->bytesRead);
                PUSH_BUF(input_queue)

                internal_state = 0;
                flag = 0;
            }


        }else{

            //printf("--%ld",GetLastError());
            }

        }while(flag);

        //ClearCommError(this->port_handler,&(this->errors),&(this->status));

        //printf("Sono rimasti dei byte: %ld\n",this->status.cbInQue );


    return TRUE;

}

BOOL SerialHandler::FlushBuffer()
{

    PurgeComm(this->port_handler,PURGE_RXCLEAR);

    BOOL bErrorFlag;
    char discard_read;
    ClearCommError(this->port_handler,&(this->errors),&(this->status));
    int bytes_pending, bufempty;
    bytes_pending = this->status.cbInQue;
    printf("Sono rimasti dei byte: %ld\n", bytes_pending );
    int i = 0;

    if(bytes_pending == 0) bufempty = 1;

    while(!bufempty)
    {
        bErrorFlag = ReadFile(this->port_handler,&discard_read,1,&(this->bytesRead),NULL);
        if(FALSE==bErrorFlag)
        {
            printf("Error: %ld",GetLastError());
        }
        ClearCommError(this->port_handler,&(this->errors),&(this->status));
        i++;
        if(this->status.cbInQue == 0) bufempty = 1;

    }

    printf("Bytes flushed: %d",i);

    return true;

}
