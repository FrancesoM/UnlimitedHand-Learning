/*****************************************************************************
* NAME : SimpleCOM.h
* DESC : Header file for SimpleCOM.cpp
* DATE : 7/15/2003
* PGMR : Y. Bai
*****************************************************************************/
#ifndef SIMPLECOM_H_
#define SIMPLECOM_H_
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>
#define MAX_MENU 7
#define MAX_STRING 256
#define NOPARITY 0
#define ONESTOPBIT 0
#define RTS_CONTROL_DISABLE 0x00
#define RTS_CONTROL_ENABLE 0x01
#define DTR_CONTROL_DISABLE 0x00
#define DTR_CONTROL_ENABLE 0x01
#define msg(info) MessageBox(NULL, info, "", MB_OK)

#define DISPLAY(buf) for(int KK = 0;KK < 210;KK++) printf("%02x ",buf[KK]); printf("\n");

#define MOVEUP      0
#define MOVDOWN     1
#define ROTOUT      2
#define ROTIN       3
#define HANDOPEN    4
#define HANDCLOSE   5
#define EXITPROG    10
#define NULLSELECTION 11

//Structure contains some parameters needed to set up and configure the serial port to be tested.
typedef struct
{
	unsigned long ulCtrlerID;
	char cEcho;
	char cEORChar;
	long lTimeout;
	long lBaudRate;
	long lDataBits;
	HANDLE h_Port;
}SerialCreate, *pSerialCreate;

//Structure that contains parameters necessary for the PortRead() function to receive data from the serial port.
typedef struct
{
	__int8 unsigned pcBuffer[210];
	BYTE bByte;
	int iMaxChars;
	int piNumRcvd;
	char cTermChar;
	HANDLE handlePort;
}CommPortClass;

//enum is used so that each number greater than zero is an error
typedef enum
{
	OK = 0, /* no error */
	EC_TIMEOUT,
	EC_FOPEN,
	EC_INVAL_CONFIG,
	EC_TIMEOUT_SET,
	EC_RECV_TIMEOUT,
	EC_EXIT_CODE,
	EC_WAIT_SINGLEOBJ,
	EC_INVALIDPORT,
	EC_WRITE_FAIL,
	EC_READ_FAIL,
	EC_TEST_FAIL,
	EC_CREATE_THREAD,
	EC_PORT_INITDONE,
	EC_UNKNOWNERROR
}ERR_CODE;

//Functions to communicate with the serial driver and perform such interfacing tasks as:
//Initialize the port
ERR_CODE PortInitialize(char const cPort[], pSerialCreate pCreate);
//Writing to the port
ERR_CODE PortWrite(HANDLE handPort, __int8 unsigned bByte, int NumByte);
//Reading from the port
ERR_CODE PortRead(CommPortClass *hCommPort);
//Handle the PortRead funciton, to avoid the dead cycle of the port when
//executing the WaitCommEvent() system function
void WINAPI ThreadFunc(void* hCommPorts);

//These last three functions are a middle layer that will call the previous functions to access the serial port to fullfill the desired tasks.
int getMenuItem(unsigned char mPort);
ERR_CODE SetupPort(char const comPortName[]);
ERR_CODE AcquireMovement(BOOL display);
#endif



