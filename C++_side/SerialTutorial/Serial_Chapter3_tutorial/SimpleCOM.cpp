/*****************************************************************************
* NAME : SimpleCOM.cpp
* DESC : Simple serial port test program - single loop
* DATE : 7/15/2003
* PGMR : Y. Bai
*****************************************************************************/
#include "SimpleCOM.h"
#include "Menu.h"
int main()
{
	int index;
	//Boolean variable used to understed whether the loop continues to run or stop
	bool select = TRUE;
	//receive user selection
	char userInput[16];
	__int8 movement;
	ERR_CODE ecRet = OK;
	unsigned char movement_code;
	char const comPortName[] = "\\\\.\\COM10";
	char const fileName[] = "BinaryDataset.bin";
	char const mode[] = "wb";
	TestPassed = FALSE;


	//File to which write the received characters
    binaryFile = fopen( fileName, mode );
	//Continue to test as long as the process is free of errors.

	//Put a name for the dataset
	char name[NAMELENGTH];
	//Write all zeros, then scanf will overwrite.
	for(int N = 0;N < NAMELENGTH; N++) name[N] = 0;

	scanf("%s",name);
    //Fill the header informations. Header will have this structure:
    //** REMEMBER THAT ALL VALUES ARE WRITTEN AS LSB -> MSB in the file.
    //** "NAME SECTION" Bytes from 0 to 50(excluded): name, each byte is a char, end is "\n"
    //** "SIZE SECTION" Bytes 50-51-52-53: integer number for acquisitions, initialized as zero since at this time we don't know how many acquisition we'll do
    //** Bytes 53-100(excluded): reserved for future implementations, for example change the endiannes.
    //** From 100 to end, acquisitions. Each acquisition has 200*8 values, which are 200*8*2 bytes + 1 byte that can be read as a char that
    //** carries information about the kind of movement. We might find a easy way to retrieve data from this file so if the format is:
    //** typeByte - 200*8*2 dataBytes - typeByte - 200*8*2 dataBytes - .... and let's call 200*8*2 = D, we know that the n-th typeBytes will be read
    //** at the address offset_data_start + (D+1)*n (remember that n starts from 0). and the n-th chunk of dataBytes will be read at the address
    //** offset_data_start + (D+1)*n + 1 up to the address offset_data_start + (D+1)*n + (D+1)*(n+1) (excluded)

    int offset;
    //Some macro helps to set the correct offset

    //Write the name on the file
    NAMEOFFSET(offset)
        fseek(binaryFile,offset,SEEK_SET);
        for(int pos_in_name = 0;pos_in_name < NAMELENGTH; pos_in_name++) fwrite((void*)&name[pos_in_name],sizeof(char),1,binaryFile);

    //Write all zeros to the size section, since this will be updated after quitting the while loop
    SIZEOFFSET(offset)
        fseek(binaryFile,offset,SEEK_SET);
        char filler = 0;
        for(int pos_in_size = 0; pos_in_size < SIZELEGHT; pos_in_size++) fwrite((void*)&filler,sizeof(char),1,binaryFile);

    //Do the actual initialization of the port.
    ecRet = SetupPort(comPortName);
    if (ecRet)
    {
        //Break the while if no successfull initialization
        select = FALSE;
    }

    unsigned int counter_of_movements = 0;

    //Positioning on the file where the data must start
    DATAOFFSET(offset)
        fseek(binaryFile,offset,SEEK_SET);

	while(select)
	{
		printf("\n");
        //Print the entries of the menu
		for (index = 0; index < MAX_MENU; index++)
		{
			printf(menuData[index]);
		}
		printf(menuTitle[0]);
		//After displaying the menu, use the scanf to get the user selection
		scanf("%s", userInput);
		movement_code = (unsigned char)userInput[0];
		//Function to translate the user decision into the actual name of the port.
		//let's say the user has decided for "10", the associated com port is ////.//COM10/
		movement = getMenuItem(movement_code);

		//printf("select = %s\n", comPort);
		if ( movement == EXITPROG || movement == NULLSELECTION )
			select = FALSE;
		else
		{
		    //write to the file the choice
            fwrite((void*)&movement, sizeof(__int8), 1 ,binaryFile);
		    counter_of_movements++;

			//Do the acquisition, if it is ok go on.
			ecRet = AcquireMovement(1);
			if (ecRet)
			{
				select = FALSE;
				break;
			}
		}


	}

	//char* intToByte = reinterpret_cast<char*>(counter_of_movements);
	SIZEOFFSET(offset)
        fseek(binaryFile,offset,SEEK_SET);
	unsigned char BytesOfInt;

	for(int writeIntCounter = 0; writeIntCounter<sizeof(int); writeIntCounter++)
    {
        BytesOfInt = ( (counter_of_movements >> writeIntCounter*8) & 0xff );
        fwrite((void*)&BytesOfInt, sizeof(char), 1, binaryFile);
    }

	CloseHandle(hPort);
	fclose(binaryFile);

	return 0;

}

ERR_CODE SetupPort(char const cPort[])
{
	ERR_CODE ecRet = OK;
	pSerialCreate pParam;
	pParam = new SerialCreate;
	pParam->lBaudRate = BAUD_RATE;
	pParam->lDataBits = NUM_BITS;
	pParam->lTimeout = TIME_OUT;

	ecRet = PortInitialize(cPort, pParam);
	if (ecRet != OK)
		printf("ERROR in PortInitialize()!\n");
	else
	{
	    //Param is a struct used internally to this function to set up the handle.
	    //Since the parameters, once set, are stored in some configuration files on windows
	    //we can delete the parameters in our program, the only thing that must remain is the handler,
	    //which is a unique identifier to the port. hPort is indeed a global variable, and once it is
	    //set here, it remains alive for the whole life of the program. All the other functions that wants
	    //to use the comPort just need this handle.
		hPort = pParam->h_Port;
	}
	delete pParam;
	return ecRet;
}


ERR_CODE AcquireMovement(BOOL display)
{
	__int8 unsigned sByte = 0x73;
	int numByte = NUM_BYTE;//, MaxByte = MAX_BYTE;
	ERR_CODE ecRet = OK;
	CommPortClass* comPort = new CommPortClass;
	comPort->handlePort = hPort;
	comPort->iMaxChars = NUM_BYTE;
	comPort->binaryFile = binaryFile;

    //Start communication
    ecRet = PortWrite(hPort, sByte, numByte);
    if (ecRet)
    {
        printf("PortWrite() is failed\n");
        TestPassed = FALSE;
        CloseHandle(hPort);
        return EC_WRITE_FAIL;
    }


    //Read the incoming stream
    ecRet = PortRead(comPort);
    //The way this program behave is read until it happens a timeout event,
    //Therefore each error different from time out is a problem and the port should be
    //closed. If instead the error is timeout, everything's ok and we can keep acquiring movements.
    if (ecRet != EC_RECV_TIMEOUT)
    {
        printf("PortRead() is failed\n");
        TestPassed = FALSE;
        CloseHandle(hPort);
        return EC_READ_FAIL;
    }

    ecRet = OK;

	delete comPort;
	return ecRet;
}

__int8 getMenuItem(unsigned char mPort)
{
	__int8 ret;
	switch (mPort)
	{
	case 'A':
	case 'a': ret = MOVEUP;
			break;
	case 'B':
	case 'b': ret = MOVDOWN;
			break;
	case 'C':
	case 'c': ret = ROTOUT;
			break;
	case 'D':
	case 'd': ret = ROTIN;
			break;
	case 'E':
	case 'e': ret = HANDOPEN;
			break;
	case 'F':
	case 'f': ret = HANDCLOSE;
			break;

	case 'X':
	case 'x': ret = EXITPROG;
			break;
	default: printf("Invalid Selection\n");
	ret = NULLSELECTION;
	}
	return ret;
}




