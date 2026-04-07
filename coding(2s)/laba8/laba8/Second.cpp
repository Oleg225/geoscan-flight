#include <iostream>
#include "Header2.h"
#include <string>
using namespace std;

bool isAgeInRange(int currentYear, int birthYear, int birthMonth, int birthDay, int minAge, int maxAge) {
    int age = currentYear - birthYear;
    if (age < minAge || age > maxAge) return false;
    return true;
}

void Can_war3(student list[], int size) {
    bool found = false;
    for (int i = 0; i < size; i++) {
        if (list[i].gender == 'M' && isAgeInRange(2025, list[i].birthday.year, list[i].birthday.month, list[i].birthday.day, 18, 27)) {
            cout << list[i].last_name << endl;
            found = true;
        }
    }
    if (!found) {
        cout << "No matching students found." << endl;
    }
}

int main() {
    student students[] = {
        {"Alice", "Johnson", 'M', {2006, 05, 21}},
        {"Bob", "Smith", 'M', {2001, 12, 24}},
        {"Charlie", "Brown", 'F', {2003, 05, 15}},
        {"David", "Williams", 'M', {2002, 12, 17}},
        {"Eve", "Jones", 'F', {2001, 03, 04}},
        {"Frank", "Garcia", 'F', {1999, 03, 06}},
        {"Grace", "Martinez", 'M', {1993, 01, 21}},
        {"Hank", "Davis", 'F', {2011, 07, 16}},
        {"Ivy", "Rodriguez", 'M', {1999, 11, 11}}
    };

    int size = sizeof(students) / sizeof(students[0]);
    Can_war3(students, size);
}
