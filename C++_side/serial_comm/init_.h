#ifndef INIT__H_INCLUDED
#define INIT__H_INCLUDED

#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include <tchar.h>

#define CHECK(x,y,msg) if(x!=y){ printf("%s\n",msg);

//This function does the initialization work, and set baudrate and other
//options for the serial comm.
int init_serial_port(char* port_name, HANDLE& port_handler);

//This function does the writing of a character to a port
BOOL WriteAChar(char* ch, HANDLE& hComm, DWORD* errors, COMSTAT* status);

#endif // INIT__H_INCLUDED
