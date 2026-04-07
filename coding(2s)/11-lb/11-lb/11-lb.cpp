#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <iomanip>

using namespace std;

class Customer {
private:
    string lastName;
    string firstName;
    string cardNumber;
    string productName;
    double purchasePrice;

public:
    // Конструктор
    Customer(string last, string first, string card, string product, double price)
        : lastName(last), firstName(first), cardNumber(card), productName(product), purchasePrice(price) {
    }

    // Геттеры
    string getLastName() const { return lastName; }
    string getFirstName() const { return firstName; }
    string getCardNumber() const { return cardNumber; }
    string getProductName() const { return productName; }
    double getPurchasePrice() const { return purchasePrice; }

    // Вывод информации о покупке
    void printInfo() const {
        cout << lastName << " " << firstName
            << " (карта: " << cardNumber << "): "
            << productName << " - " << purchasePrice << " руб." << endl;
    }
};

int main() {
    setlocale(LC_ALL, "Russian");

    // Создаем список покупателей
    vector<Customer> customers = {
        Customer("Petrov", "Иван", "123456789012", "Ноутбук", 45000),
        Customer("Петров", "Петр", "234567890123", "Смартфон", 25000),
        Customer("Сидоров", "Алексей", "345678901234", "Планшет", 18000),
        Customer("Ивановов", "Сергей", "456789012345", "Наушники", 5000),
        Customer("Кузнецова", "Мария", "567890123456", "Фотоаппарат", 32000),
        Customer("Иванововово", "Дмитрий", "678901234567", "Монитор", 15000),
        Customer("Смирнова", "Ольга", "789012345678", "Принтер", 8000)
    };

    // Вычисляем среднюю стоимость покупок
    double total = 0;
    for (const auto& customer : customers) {
        total += customer.getPurchasePrice();
    }
    double average = total / customers.size();
    cout << fixed << setprecision(2);
    cout << "\nСредняя стоимость покупок: " << average << " руб." << endl;

    // Запрашиваем фамилию покупателя
    string searchLastName;
    cout << "\nВведите фамилию покупателя: ";
    cin >> searchLastName;

    // Создаем файл с покупками этого клиента
    ofstream outFile(searchLastName + "_purchases.txt");
    if (!outFile) {
        cerr << "Ошибка при создании файла!" << endl;
        return 1;
    }

    outFile << "Список покупок покупателя " << searchLastName << ":\n";
    outFile << "----------------------------------------\n";

    bool found = false;
    for (const auto& customer : customers) {
        if (customer.getLastName() == searchLastName) {
            found = true;
            outFile << customer.getProductName() << " - "
                << customer.getPurchasePrice() << " руб.\n";
        }
    }

    if (!found) {
        outFile << "Покупатель с такой фамилией не найден.\n";
        cout << "Покупатель с фамилией '" << searchLastName << "' не найден." << endl;
    }
    else {
        cout << "Список покупок сохранен в файл '" << searchLastName << "_purchases.txt'" << endl;
    }

    outFile.close();

    return 0;
}