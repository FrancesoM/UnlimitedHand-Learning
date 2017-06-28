First:  The queue "input_data_queue" is the global data structure that allow the communication.
        The mutex "mut" is the global MUTualEXclusive data structure that ensure the correct communication.
        The condition_variable "data_cond" is used to notify the other threads that are listening

Second: The guard_lock is an object that locks the mutex on calling and unlocks it when the object is destroyed,
        and that's what happens at each iteration in the while loop.

READ:   Before reading a value from the serial port the "read" thread keeps exclusive access to the queue, so that
        "process" must wait. After writing to the queue it sends a notification to the other thread "process" and
        unlocks the mutex.

PROC:   This is a bit tricky. Let's start from the documentation from cppreference.com of std::condition_variable::wait
        Parameters: ( std::unique_lock<std::mutex>& lock, Predicate pred )
        So it wants a lock, which in the code is "lk" and a predicate, which is our lambda function. The lambda
        is very simple: it just returns False if the queue is empty and True if the queue has data.

        Going on with the documentation:
        "wait" causes the current thread to block until the condition variable is notified or a spurious wakeup occurs,
        optionally looping until some predicate is satisfied. It is equivalent to:

        while (!pred()) {
            wait(lock);
        }

        And wait(lock) means:
        Atomically releases lock, blocks the current executing thread. The thread will be unblocked when notify_all()
        or notify_one() is executed

        So this expands in this code as: while(!(!(is_empty))) the two "!" cancels out and therefore the waiting should
        be continued if the queue.is_empty() returns true.

        The documentation also say that the lock must be locked before passing it to the function. That's why we pass a
        unique_lock instead of a lock_guard, because "wait" is in charge of locking/unlocking the mutex.

        The final behavior of the thread is to stay in a wait state until it receives a notification, check if the queue is
        empty. If not, acquire exclusive access to the queue and pop out elements in order to process them.

Note:   This is the first implementation. That dictates the bone-structure of the whole process, then major changes
        could happen regarding the functionalities of the threads.
		
		
		
****************************************** Version 0.03b *******************************************************
		
		- Now you can pass as a parameter the name the txt file should have. 
		- If the name is not specified, the file will be named "default.txt"
		- If the time is not specified, 1s is the default time. 
		
****************************************** Version 0.03 *******************************************************

        Values are printed on a file instead of the terminal.
		
****************************************** Version 0.02 *******************************************************

        Now with the command line argument -t T you can specify the duration T (in milliseconds) of the acquisition

****************************************** Version 0.01 *******************************************************

        The payload for shifting bytes and recreate values is in charge of the "read" thread. The process
        just print data on the screen.



*/