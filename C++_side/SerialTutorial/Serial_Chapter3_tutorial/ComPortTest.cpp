/*****************************************************************************
* NAME: ComPortTest.cpp
* DESC: Support C++ file for SimpleCOM.cpp
* DATE: 7/15/2003
* PGMR: Y. Bai
*****************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include "SimpleCOM.h"
ERR_CODE PortInitialize(char const comPortName[], pSerialCreate pCreate)
{
	HANDLE hPort;
	DWORD dwError;
	DCB PortDCB;
	ERR_CODE ecStatus = OK;
	COMMTIMEOUTS CommTimeouts;
	unsigned char dBit;

	printf("Opening serial port %s\n",comPortName);


	// Open the serial port.
	hPort = CreateFile( comPortName, // Pointer to the name of the port
						GENERIC_READ | GENERIC_WRITE, // Access (read/write) mode
						0, // Share mode
						NULL, // Pointer to the security attribute
						OPEN_EXISTING, // How to open the serial port
						0, // Port attributes
						NULL); // Handle to port with attribute copy
						// If it fails to open the port, return error.
	if ( hPort == INVALID_HANDLE_VALUE )
	{
		// Could not open the port.
		dwError = GetLastError();
		msg("Unable to open the port");
		CloseHandle(hPort);
		return EC_FOPEN;
	}
	PortDCB.DCBlength = sizeof(DCB);
	// Get the default port setting information.
	GetCommState(hPort, &PortDCB);
	// Change the DCB structure settings.
	PortDCB.BaudRate = pCreate->lBaudRate; // Current baud rate
	PortDCB.fBinary = TRUE; // Binary mode; no EOF check
	PortDCB.fParity = TRUE; // Enable parity checking.
	PortDCB.fOutxCtsFlow = FALSE; // No CTS output flow control
	PortDCB.fOutxDsrFlow = FALSE; // No DSR output flow control
	PortDCB.fDtrControl = DTR_CONTROL_ENABLE; // DTR_CONTROL
	PortDCB.fDsrSensitivity = FALSE; // DSR sensitivity
	PortDCB.fTXContinueOnXoff = TRUE; // XOFF continues Tx
	PortDCB.fOutX = FALSE; // No XON/XOFF out flow control
	PortDCB.fInX = FALSE; // No XON/XOFF in flow control
	PortDCB.fErrorChar = FALSE; // Disable error replacement.
	PortDCB.fNull = FALSE; // Disable null stripping.
	PortDCB.fRtsControl = RTS_CONTROL_ENABLE; // RTS_CONTROL
	PortDCB.fAbortOnError = FALSE; // Don’t abort reads/writes error.
	dBit = (unsigned char)pCreate->lDataBits;
	PortDCB.ByteSize = dBit; // Number of bits/bytes, 4-8
	PortDCB.Parity = NOPARITY; // 0-4=no,odd,even,mark,space
	PortDCB.StopBits = ONESTOPBIT; // 0,1,2 = 1, 1.5, 2
	// Configure the port according to the specifications of the DCB structure.
	if (!SetCommState (hPort, &PortDCB))
	{
		// Could not create the read thread.
		dwError = GetLastError();
		msg("Unable to configure the serial port");
		return EC_INVAL_CONFIG;
	}
	// Retrieve the time-out parameters for all read and write operations on the port.
	GetCommTimeouts(hPort, &CommTimeouts);

	// Change the COMMTIMEOUTS structure settings.
	CommTimeouts.ReadIntervalTimeout = MAXDWORD;
	CommTimeouts.ReadTotalTimeoutMultiplier = 0;
	CommTimeouts.ReadTotalTimeoutConstant = 0;
	CommTimeouts.WriteTotalTimeoutMultiplier = 10;
	CommTimeouts.WriteTotalTimeoutConstant = 1000;
	// Set the time-out parameters for all read and write operations on the port.
	if (!SetCommTimeouts (hPort, &CommTimeouts))
	{
	// Could not create the read thread.
		dwError = GetLastError();
		msg("Unable to set the time-out parameters");
		return EC_TIMEOUT_SET;
	}
	EscapeCommFunction(hPort, SETDTR);
	EscapeCommFunction(hPort, SETRTS);
	pCreate->h_Port = hPort;
	return ecStatus;
}
ERR_CODE PortWrite(HANDLE handPort, __int8 unsigned bByte, int NumByte)
{
	DWORD dwError;
	DWORD dwNumBytesWritten;
	ERR_CODE ecStatus = OK;
	if (!WriteFile (handPort, // Port handle
					&bByte, // Pointer to the data to write
					NumByte, // Number of bytes to write
					&dwNumBytesWritten, // Pointer to the number of bytes written
					NULL)) // Must be NULL for Windows CE
	{
		// WriteFile failed. Report error.
		dwError = GetLastError ();
		msg("ERROR in PortWrite ..");
		return EC_WRITE_FAIL;
	}
	printf("Bytes written %ld\n",dwNumBytesWritten);
	return ecStatus;
}
ERR_CODE PortRead(CommPortClass *hCommPort)
{
	HANDLE hThread; // handler for port read thread
	DWORD IDThread;
	DWORD Ret, ExitCode;
	DWORD dTimeout = 1000; // define time out value: 5 sec.
	ERR_CODE ecStatus = OK;
	DWORD dwError;
	COMSTAT comStatus;
	if (!(hThread = CreateThread(NULL, // no security attributes
					0, // use default stack size
					(LPTHREAD_START_ROUTINE) ThreadFunc,
					(LPVOID)hCommPort, // parameter to thread funciton
					CREATE_SUSPENDED, // creation flag - suspended
					&IDThread) ) ) // returns thread ID
	{
		msg("Create Read Thread failed");
		return EC_CREATE_THREAD;
	}
	ResumeThread(hThread); // start thread now
		//This tab to emphatize the fact that the thread has started.
		Ret = WaitForSingleObject(hThread, dTimeout);
		if (Ret == WAIT_OBJECT_0)
		{
			// data received & process it... Need to do nothing
			// Because the data has been stored in the hCommPort in Thread Func.
			// close thread handle

			//DISPLAY(hCommPort->pcBuffer)
			CloseHandle(hThread);
		}
		else if (Ret == WAIT_TIMEOUT)
		{
			// time out happened, warning & kill thread
			Ret = GetExitCodeThread(hThread, &ExitCode);
			ClearCommError(hCommPort->handlePort,&dwError,&comStatus);
			printf("Bytes remained in the port: %d\n",comStatus.cbInQue);
			//msg("Time out happened in PortRead() ");
			if (ExitCode == STILL_ACTIVE)
			{
				TerminateThread(hThread, ExitCode);
				CloseHandle(hThread);
				printf("Error from line 152: %d\n",ecStatus);
				return EC_RECV_TIMEOUT;
			}
			else
			{
				CloseHandle(hThread);
				msg("ERROR in GetExitCodeThread: != STILL_ACTIVE ");
				ecStatus = EC_EXIT_CODE;
			}
		}
		else
		{
		msg("ERROR in WaitFor SingleObject ");
		ecStatus = EC_WAIT_SINGLEOBJ;
		}
	printf("Error from line 166: %d\n",ecStatus);

	return ecStatus;
}
void WINAPI ThreadFunc(void* hCommPorts)
{
	DWORD dwError;
	BOOL bResult;
	BOOL garbageFlushed = false;
	BYTE garbageByte;
	int  garbageSeek = 0;
	int nTotRead = 0;
	DWORD dwCommModemStatus, dwBytesTransferred;
	CommPortClass* CommPorts;
	ERR_CODE ecStatus = OK;
	COMSTAT comStatus;


	CommPorts = (CommPortClass* )hCommPorts;
	// Specify a set of events to be monitored for the port.
	SetCommMask(CommPorts->handlePort, EV_RXCHAR);
	// Wait for an event to occur for the port.
	WaitCommEvent(CommPorts->handlePort, &dwCommModemStatus, 0);
	// Re-specify the set of events to be monitored for the port.
	SetCommMask(CommPorts->handlePort, EV_RXCHAR );

    //Flush garbage Routine
//    while(!garbageFlushed)
//    {
//    	if (dwCommModemStatus & EV_RXCHAR || dwCommModemStatus & EV_RLSD)
//        {
//            ReadFile(CommPorts->handlePort, &garbageByte, 1, &dwBytesTransferred, 0);
//            if(garbageByte == 0x21) garbageSeek++;
//            else garbageSeek = 0;
//
//            if(garbageSeek == 3) //we found the three " 0x21 0x21 0x21 "
//            {
//                garbageFlushed = 1; //flush the first line and align to the correct offset in the serial buffer.
//                for(int flush = 0;flush<16;flush++)
//                {
//                    ReadFile(CommPorts->handlePort, &garbageByte, 1, &dwBytesTransferred, 0);
//                }
//            }
//        }
//    }

        //Now that we are aligned to the correct start of the packet, read chunks of correct data.
    if (dwCommModemStatus & EV_RXCHAR || dwCommModemStatus & EV_RLSD)
    {
        do{
                // received the char_event
                // Read the data from the serial port.
                bResult = ReadFile(CommPorts->handlePort, &CommPorts->bByte, 1, &dwBytesTransferred, 0);
                if(dwBytesTransferred==1) printf("%02x  ",CommPorts->bByte); //n_ transfered: %ld, totale: %d\n  ",garbageByte,dwBytesTransferred,nTotRead);
                //ClearCommError(CommPorts->handlePort,&dwError,&comStatus);
                //;
            if (!bResult)
            {
                printf("Unable to read the port\n");
                switch (dwError = GetLastError())
                {
                case ERROR_HANDLE_EOF:
                    printf("Serial Receive Failed\n");
                break;
                }
            }
            else
            {
                // store the data read.
                //CommPorts->bByte = Byte;
                nTotRead+=dwBytesTransferred;
                //printf("%d",nTotRead);
            }
        }while(nTotRead<=10+200*16);

        //PurgeComm(CommPorts->handlePort, PURGE_RXCLEAR);
        //printf("\n",garbageByte);
    }
return;
}
