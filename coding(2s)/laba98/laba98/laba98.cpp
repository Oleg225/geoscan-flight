#include <iostream>
#include <fstream> 
#include <sstream> 

using namespace std;


int sumOfNumbersInLine(const string& line) {
    stringstream ss(line);
    int number;
    int sum = 0;
    while (ss >> number) { 
        sum += number;     
    }
    return sum;
}

int main() {
   
    ifstream file1("f1.txt");
    ifstream file2("f2.txt");

    if (!file1.is_open() || !file2.is_open()) {
        cout << "Ошибка открытия файлов!" << endl;
        return 1;
    }


    ofstream file3("f3.txt");
    if (!file3.is_open()) {
        cout << "Ошибка создания файла f3.txt!" << endl;
        return 1;
    }

    string line1, line2;
    bool hasMoreLines = true;

    while (hasMoreLines) {
        hasMoreLines = false;


        if (getline(file1, line1)) {
            int sum1 = sumOfNumbersInLine(line1);
            file3 << sum1 << endl;              
            hasMoreLines = true;                 
        }

       
        if (getline(file2, line2)) {
            int sum2 = sumOfNumbersInLine(line2); 
            file3 << sum2 << endl;            
            hasMoreLines = true;                 
        }
    }

   
    file1.close();
    file2.close();
    file3.close();

    cout << "Correct!" << endl;
    return 0;
}