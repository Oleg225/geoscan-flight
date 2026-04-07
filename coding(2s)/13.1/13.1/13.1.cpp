#include <iostream>
#include <vector>
#include <chrono>
#include <random>
#include <algorithm>

using namespace std;
using namespace std::chrono;

//  Алгоритмы сортировки 

// Пузырьковая сортировка
void bubbleSort(vector<int>& arr, int& swaps) {
    int n = arr.size();
    for (int i = 0; i < n - 1; ++i) {
        for (int j = 0; j < n - i - 1; ++j) {
            if (arr[j] > arr[j + 1]) {
                swap(arr[j], arr[j + 1]);
                swaps++;
            }
        }
    }
}

// Сортировка выбором
void selectionSort(vector<int>& arr, int& swaps) {
    int n = arr.size();
    for (int i = 0; i < n - 1; ++i) {
        int min_idx = i;
        for (int j = i + 1; j < n; ++j) {
            if (arr[j] < arr[min_idx]) {
                min_idx = j;
            }
        }
        if (min_idx != i) {
            swap(arr[i], arr[min_idx]);
            swaps++;
        }
    }
}

// Сортировка Шелла
void shellSort(vector<int>& arr, int& swaps) {
    int n = arr.size();
    for (int gap = n / 2; gap > 0; gap /= 2) {
        for (int i = gap; i < n; ++i) {
            int temp = arr[i];
            int j;
            for (j = i; j >= gap && arr[j - gap] > temp; j -= gap) {
                arr[j] = arr[j - gap];
                swaps++;
            }
            arr[j] = temp;
        }
    }
}

//  Генерация разных типов данных 

// 1. Неотсортированный массив (рандомчик)
vector<int> generateRandomArray(int size) {
    vector<int> arr(size);
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> dis(1, 10000);
    for (int& num : arr) {
        num = dis(gen);
    }
    return arr;
}

// 2. Частично отсортированный (50/50)
vector<int> generatePartiallySortedArray(int size) {
    vector<int> arr = generateRandomArray(size);
    sort(arr.begin(), arr.begin() + size / 2);
    return arr;
}

// 3. Почти отсортированный (немножечко искоженный массив)
vector<int> generateAlmostSortedArray(int size) {
    vector<int> arr(size);
    for (int i = 0; i < size; ++i) {
        arr[i] = i + 1;
    }
    // Перемешиваем 10% элементов
    random_device rd;
    mt19937 gen(rd());
    for (int i = 0; i < size / 10; ++i) {
        int idx1 = gen() % size;
        int idx2 = gen() % size;
        swap(arr[idx1], arr[idx2]);
    }
    return arr;
}

// 4. Обратно отсортированный (убывающий)
vector<int> generateReverseSortedArray(int size) {
    vector<int> arr(size);
    for (int i = 0; i < size; ++i) {
        arr[i] = size - i;
    }
    return arr;
}

//  Замер времени  
void measureSortingTime(const string& sortName, void (*sortFunc)(vector<int>&, int&), vector<int> arr) {
    int swaps = 0;
    auto start = high_resolution_clock::now();
    sortFunc(arr, swaps);
    auto stop = high_resolution_clock::now();
    auto duration = duration_cast<microseconds>(stop - start);
    cout << sortName << ":\t" << duration.count() << " мкс\tПерестановок: " << swaps << endl;
}

int main() {
    setlocale(LC_ALL, "Russian"); 

    const int SIZE = 1000; 

    cout << "=== Тест на неотсортированном массиве ===" << endl;
    vector<int> randomArr = generateRandomArray(SIZE);
    measureSortingTime("Пузырьковая", bubbleSort, randomArr);
    measureSortingTime("Выбором    ", selectionSort, randomArr);
    measureSortingTime("Шелла      ", shellSort, randomArr);

    cout << "\n=== Тест на частично отсортированном массиве ===" << endl;
    vector<int> partialArr = generatePartiallySortedArray(SIZE);
    measureSortingTime("Пузырьковая", bubbleSort, partialArr);
    measureSortingTime("Выбором    ", selectionSort, partialArr);
    measureSortingTime("Шелла      ", shellSort, partialArr);

    cout << "\n=== Тест на почти отсортированном массиве ===" << endl;
    vector<int> almostArr = generateAlmostSortedArray(SIZE);
    measureSortingTime("Пузырьковая", bubbleSort, almostArr);
    measureSortingTime("Выбором    ", selectionSort, almostArr);
    measureSortingTime("Шелла      ", shellSort, almostArr);

    cout << "\n=== Тест на обратно отсортированном массиве ===" << endl;
    vector<int> reverseArr = generateReverseSortedArray(SIZE);
    measureSortingTime("Пузырьковая", bubbleSort, reverseArr);
    measureSortingTime("Выбором    ", selectionSort, reverseArr);
    measureSortingTime("Шелла      ", shellSort, reverseArr);

    cout << "\n=== Выводы ===" << endl;
    cout << "1. Пузырьковая сортировка быстра на почти упорядоченных данных, но медленна в остальных случаях." << endl;
    cout << "2. Сортировка выбором всегда работает за O(n²), независимо от данных." << endl;
    cout << "3. Сортировка Шелла — самая быстрая из трёх и хорошо работает на любых данных." << endl;

    return 0;
}