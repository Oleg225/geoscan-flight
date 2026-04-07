#include <iostream>
#include <fstream> 
#include <limits>  
#include <iomanip> 

using namespace std;

int main() {

    ofstream outFile("data_types_info.txt");
    if (!outFile.is_open()) {
        cout << "Ошибка открытия файла!" << endl;
        return 1;
    }

    outFile << setw(20) << left << "Тип данных"
        << setw(15) << "Размер (байт)"
        << setw(20) << "Минимальное значение"
        << setw(20) << "Максимальное значение" << endl;

    outFile << setw(20) << left << "char"
        << setw(15) << sizeof(char)
        << setw(20) << int(numeric_limits<char>::min())
        << setw(20) << int(numeric_limits<char>::max()) << endl;

    outFile << setw(20) << left << "short int"
        << setw(15) << sizeof(short int)
        << setw(20) << numeric_limits<short int>::min()
        << setw(20) << numeric_limits<short int>::max() << endl;

    outFile << setw(20) << left << "unsigned short int"
        << setw(15) << sizeof(unsigned short int)
        << setw(20) << numeric_limits<unsigned short int>::min()
        << setw(20) << numeric_limits<unsigned short int>::max() << endl;

    outFile << setw(20) << left << "int"
        << setw(15) << sizeof(int)
        << setw(20) << numeric_limits<int>::min()
        << setw(20) << numeric_limits<int>::max() << endl;

    outFile << setw(20) << left << "unsigned int"
        << setw(15) << sizeof(unsigned int)
        << setw(20) << numeric_limits<unsigned int>::min()
        << setw(20) << numeric_limits<unsigned int>::max() << endl;

    outFile << setw(20) << left << "long int"
        << setw(15) << sizeof(long int)
        << setw(20) << numeric_limits<long int>::min()
        << setw(20) << numeric_limits<long int>::max() << endl;

    outFile << setw(20) << left << "unsigned long int"
        << setw(15) << sizeof(unsigned long int)
        << setw(20) << numeric_limits<unsigned long int>::min()
        << setw(20) << numeric_limits<unsigned long int>::max() << endl;

    outFile << setw(20) << left << "float"
        << setw(15) << sizeof(float)
        << setw(20) << numeric_limits<float>::min()
        << setw(20) << numeric_limits<float>::max() << endl;

    outFile << setw(20) << left << "double"
        << setw(15) << sizeof(double)
        << setw(20) << numeric_limits<double>::min()
        << setw(20) << numeric_limits<double>::max() << endl;

    outFile << setw(20) << left << "long double"
        << setw(15) << sizeof(long double)
        << setw(20) << numeric_limits<long double>::min()
        << setw(20) << numeric_limits<long double>::max() << endl;


    outFile.close();

    cout << "Correct! Open file data_types_info.txt!" << endl;
    return 0;
}