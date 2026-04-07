#include <iostream>
#include <fstream>
#include <cstring>
#include <iomanip>

using namespace std;

struct Buyer {
    char last_name[50];
    char first_name[50];
    int card_number;
    char product[50];
    double price;
};

void createBinaryFile(const string& filename) {

    Buyer buyers[10] = {
     {"Иванов", "Иван", 1001, "Ноутбук", 99999.99},
     {"Петров", "Петр", 1002, "Смартфон", 4979.99},
     {"Сидоров", "Алексей", 1003, "Планшет", 26499.99},
     {"Смирнова", "Анна", 1004, "Наушники", 11349.99},
     {"Кузнецов", "Дмитрий", 1005, "Монитор", 19349.99},
     {"Попова", "Мария", 1006, "Клавиатура", 5911.99},
     {"Волков", "Сергей", 1007, "Мышь", 229.99},
     {"Федорова", "Ольга", 1008, "Принтер", 1239.99},
     {"Николаев", "Андрей", 1009, "Роутер", 4379.99},
     {"Павлова", "Елена", 1010, "Веб-камера", 819.99}
    };


    ofstream out(filename, ios::binary);
    if (!out) {
        cerr << "Ошибка создания файла!" << endl;
        return;
    }

    out.write(reinterpret_cast<char*>(buyers), sizeof(buyers));
    out.close();
}

void readAndPrintData(const string& filename) {
    ifstream in(filename, ios::binary);
    if (!in) {
        cerr << "Ошибка открытия файла!" << endl;
        return;
    }


    Buyer buyers[10];
    in.read(reinterpret_cast<char*>(buyers), sizeof(buyers));


    cout << left << setw(15) << "Фамилия"
        << setw(15) << "Имя"
        << setw(10) << "Карта"
        << setw(15) << "Товар"
        << "Стоимость" << endl;
    cout << string(65, '-') << endl;

    for (const auto& buyer : buyers) {
        cout << setw(15) << buyer.last_name
            << setw(15) << buyer.first_name
            << setw(10) << buyer.card_number
            << setw(15) << buyer.product
            << fixed << setprecision(2) << buyer.price << " Рублей" << endl;
    }

    in.close();
}

int main() {
    setlocale(LC_ALL, "Russian");
    const string filename = "buyers.bin";


    createBinaryFile(filename);

    readAndPrintData(filename);

    return 0;
}