#ifndef HEADER2_H 
#define HEADER2_H

#include <string>

using namespace std;


struct Date {
    int year;
    int month; 
    int day;
};

struct student {
    string First_name;
    string last_name;
    char gender; 
    Date birthday; 
};

#endif
