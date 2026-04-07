#include <iostream>
#include <clocale> 
#include "header.h"

using namespace std; 

int main() {
 
    setlocale(LC_ALL, "Russian");


    const int numberOfCustomers = 4;
    Customer customers[numberOfCustomers] = {
        {"Ivanov", "Ivan", 12345, "Laptop", 50000.0},
        {"Petrov", "Petr", 54321, "Smartphone", 30000.0},
        {"Sidorova", "Maria", 67890, "Tablet", 25000.0},
        {"Ivanov", "Ivan", 12345, "Headphones", 5000.0}
    };


    double totalPurchaseAmount[numberOfCustomers] = { 0 };

    bool processed[numberOfCustomers] = { false };

    for (int i = 0; i < numberOfCustomers; ++i) {
        if (!processed[i]) { 
            string currentCustomer = customers[i].surname + " " + customers[i].name + " (" + to_string(customers[i].cardNumber) + ")";
            double totalAmount = customers[i].purchaseAmount;


            for (int j = i + 1; j < numberOfCustomers; ++j) {
                if (customers[i].surname == customers[j].surname &&
                    customers[i].name == customers[j].name &&
                    customers[i].cardNumber == customers[j].cardNumber) {
                    totalAmount += customers[j].purchaseAmount;
                    processed[j] = true; 
                }
            }


            cout << "Customer: " << currentCustomer << ", Total purchase amount: " << totalAmount << " RUB." << endl;
        }
    }

    return 0;
}