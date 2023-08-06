#include <iostream>

int* createArray() {
    int arr[5] = {1, 2, 3, 4, 5};
    return arr;
}

int print(int *p) {
  std::cout<< *p << std::endl;
  return 0;
}

int main() {
    int* ptr = createArray();
    print(ptr);
    return 0;
}
