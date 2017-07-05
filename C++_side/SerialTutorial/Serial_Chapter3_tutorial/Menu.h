/*****************************************************************************
* NAME : Menu.h
* DESC : Header file for the menu input and menu display
* PGMR : Y. Bai
*****************************************************************************/
#define NUM_BYTE 1
#define MAX_BYTE 0x74
#define START_BYTE 0x73
#define BAUD_RATE 115200
#define NUM_BITS 8
#define TIME_OUT 3000

//Global variable used to reserve the handler when a new port is created
HANDLE hPort;
//Monitor the status of the port
bool TestPassed;

//Display the menu on the consolle screen.
const char* const menuData[] =
{   "A Movement up\n",
	"B Movement down\n",
	"C Rotation out\n",
	"D Rotation in\n",
	"E Hand open\n",
	"F Hand close\n",
    "X EXIT\n\n" };
const char* const menuTitle[] =
{ "Movement selection - Enter Selection > \n\n"};


