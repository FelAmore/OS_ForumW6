# Import modules
import threading
import random

# Parameters
LOWER_NUM = 1
UPPER_NUM = 10000
BUFFER_SIZE = 100
MAX_COUNT = 10000

# Bounded integer buffer (stack)
buffer = []
lock = threading.Lock()
condition = threading.Condition(lock)
producer_done = threading.Event()

# Function to check parity of a number
def is_even(num):
    return num % 2 == 0

# Function for producer
def producer():
    count = 0
    while count < MAX_COUNT:
        num = random.randint(LOWER_NUM, UPPER_NUM)
        with condition:
            # Wait until there is space in the buffer
            while len(buffer) >= BUFFER_SIZE:
                condition.wait()
                if producer_done.is_set():
                    return
            # Produce a random number and add it to the buffer
            buffer.append(num)
            count += 1
            print(f"Produced: {num}")
            # Put the numbers into the "all.txt" file
            with open("all.txt", "a") as f:
                f.write(str(num) + "\n")
            # Notify waiting threads that a new number is available
            condition.notify_all()
    producer_done.set()  # Notify that producer has finished producing numbers


# Function for consumer
def customer(is_even_thread):
    # Naming the files
    filename = "even.txt" if is_even_thread else "odd.txt"
    while True:
        with condition:
            # Wait until there are numbers in the buffer
            while not buffer:
                if producer_done.is_set():
                    return
                condition.wait()
            # Check the parity of the last number in the buffer
            if is_even(buffer[-1]) == is_even_thread:
                # Consume the number and put it into the corresponding file
                num = buffer.pop()
                print(f"Consumed: {num}")
                # Put the numbers into their corresponding files.
                with open(filename, "a") as f:
                    f.write(str(num) + "\n")
            else:
                # If the number doesn't match the thread type, wait for another matching number.
                condition.wait()
            # Notify waiting threads that a number has been consumed
            condition.notify_all()


# Main function
def main():
    # Create producer and customer threads
    producer_thread = threading.Thread(target=producer)
    customer_thread1 = threading.Thread(target=customer, args=(True,))
    customer_thread2 = threading.Thread(target=customer, args=(False,))

    # Start all threads
    producer_thread.start()
    customer_thread1.start()
    customer_thread2.start()

    # Wait for all threads to finish
    producer_thread.join()
    customer_thread1.join()
    customer_thread2.join()

    print("Program done executing")  # Notify users when program has ended


if __name__ == "__main__":
    main()
