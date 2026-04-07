#include<iostream>
#include "Header.h"
#include<string>
using namespace std;
string max_score(student list[]) {
	int mx_score = list[0].f_exam + list[0].s_exam + list[0].t_exam;
	string f_name;
	string l_name;
	for (int i = 0; i < 10; i++) {
		int total = list[i].f_exam + list[i].s_exam + list[i].t_exam;
		if (total > mx_score) {
			mx_score = total;
			f_name = list[i].First_name;
			l_name = list[i].last_name;

		}
	}
	return f_name;
	return l_name;
}
string name_search(student list[], string l_name) {
	string our_f_name = "Empty";
	for (int i = 0; i < 10; i++) {
		if (list[i].last_name == l_name) {
			our_f_name = list[i].First_name;
		}

	}
	return our_f_name;
}
int main() {
	student students[10] = {
		{"Alice", "Johnson", 52, 53, 78},
		{"Bob", "Smith", 74, 24, 75},
		{"Charlie", "Brown", 45, 64, 84},
		{"David", "Williams", 84, 34, 64},
		{"Eve", "Jones", 51, 68, 46},
		{"Frank", "Garcia", 84, 33, 85},
		{"Grace", "Martinez", 53, 75, 35},
		{"Hank", "Davis", 76, 35, 85},
		{"Ivy", "Rodriguez", 76, 53, 96}
	};
	cout << max_score(students) << endl;
	cout << name_search(students, "Smith");
}
