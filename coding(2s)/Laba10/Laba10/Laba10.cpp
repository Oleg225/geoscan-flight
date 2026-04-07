#include <iostream>
#include <fstream>
#include <string>
using namespace std;

struct Student {
    char name[50];
    int age;
    float avgpoint;
};

void createBinaryFile(const string& filename) {
    ofstream outFile(filename, ios::binary);
    Student students[10] = {
        {"Durov", 20, 3.5}, {"Lans", 21, 3.7}, {"Kane", 22, 3.8},
        {"Messi", 19, 3.9}, {"Elanga", 20, 3.6}, {"Burn", 21, 3.4},
        {"Mee", 22, 3.5}, {"Hank", 20, 3.1}, {"Ivy", 21, 3.2}, {"July", 22, 3.3}
    };
    outFile.write(reinterpret_cast<char*>(students), sizeof(students));
    outFile.close();
}

void readBinaryFile(const string& filename) {
    ifstream inFile(filename, ios::binary);
    Student students[10];
    inFile.read(reinterpret_cast<char*>(students), sizeof(students));
    inFile.close();
    for (const auto& student : students) {
        cout << "Name: " << student.name << ", Age: " << student.age 
             << ", AVGPoint: " << student.avgpoint << endl;
    }
}

void swapStudentsInFile(const string& filename, int index1, int index2) {
    if (index1 < 0 || index1 >= 10 || index2 < 0 || index2 >= 10) {
        cout << "Ошибка: индексы должны быть в пределах от 0 до 9." << endl;
        return;
    }
    if (index1 == index2) {
        cout << "Ошибка: индексы не должны совпадать." << endl;
        return;
    }
    fstream file(filename, ios::in | ios::out | ios::binary);
    Student student1, student2;
    
    // Чтение первого студента
    file.seekg(index1 * sizeof(Student));
    file.read(reinterpret_cast<char*>(&student1), sizeof(Student));
    
    // Чтение второго студента
    file.seekg(index2 * sizeof(Student));
    file.read(reinterpret_cast<char*>(&student2), sizeof(Student));
    
    // Запись второго студента на место первого
    file.seekp(index1 * sizeof(Student));
    file.write(reinterpret_cast<char*>(&student2), sizeof(Student));
    
    // Запись первого студента на место второго
    file.seekp(index2 * sizeof(Student));
    file.write(reinterpret_cast<char*>(&student1), sizeof(Student));
    
    file.close();
}

int main() {
    setlocale(LC_ALL, "Russian");
    string filename = "students.bin";
    createBinaryFile(filename);
    cout << "Содержимое файла до изменения:" << endl;
    readBinaryFile(filename);
    
    int index1, index2;
    cout << "Введите два индекса для обмена (от 0 до 9):" << endl;
    cin >> index1 >> index2;
    swapStudentsInFile(filename, index1, index2);
    
    cout << "Содержимое файла после изменения:" << endl;
    readBinaryFile(filename);
    return 0;
}