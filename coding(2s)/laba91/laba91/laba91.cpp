#include <iostream>
#include <fstream> 
#include <sstream> 
#include <string>  
#include <clocale> 

using namespace std;

int main() {
    
    setlocale(LC_ALL, "Russian");

   
    ifstream inputFile("C:\\Temp\\data.txt");
    if (!inputFile.is_open()) {
        cout << "Ошибка открытия файла data.txt!" << endl;
        return 1;
    }


    ofstream outputFile("C:\\Temp\\positive.txt");
    if (!outputFile.is_open()) {
        cout << "Ошибка создания файла positive.txt!" << endl;
        inputFile.close();
        return 1;
    }

    string line; 
    while (getline(inputFile, line)) { 
        stringstream ss(line);
        string numberStr; 
        bool firstNumber = true; 

        while (ss >> numberStr) { 
            int number = stoi(numberStr); 
            if (number > 0) { 
                if (!firstNumber) {
                    outputFile << " "; 
                }
                outputFile << number;
                firstNumber = false;
            }
            else { 
                if (!firstNumber) {
                    outputFile << " ";
                }
                outputFile << " "; 
                firstNumber = false;
            }
        }
        outputFile << endl; 
    }

  
    inputFile.close();
    outputFile.close();

    cout << "Pos number in file positive.txt!" << endl;
    return 0;
}