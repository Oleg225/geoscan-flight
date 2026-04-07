#include <iostream>
#include <string>
using namespace std;

struct Buyer {
    string lastName;
    string firstName;
    string cardNumber;
    string productName;
    double purchaseAmount;
    Buyer* next;

    Buyer(const string& lastName_, const string& firstName_, const string& cardNumber_,
        const string& productName_, double purchaseAmount_)
        : lastName(lastName_), firstName(firstName_), cardNumber(cardNumber_),
        productName(productName_), purchaseAmount(purchaseAmount_), next(nullptr) {
    }
};

class BuyerList {
private:
    Buyer* head;

public:
    BuyerList() : head(nullptr) {}

    void push_back(const string& lastName, const string& firstName, const string& cardNumber,
        const string& productName, double purchaseAmount) {
        Buyer* newBuyer = new Buyer(lastName, firstName, cardNumber, productName, purchaseAmount);
        if (!head) {
            head = newBuyer;
        }
        else {
            Buyer* temp = head;
            while (temp->next) {
                temp = temp->next;
            }
            temp->next = newBuyer;
        }
    }

    void print_all() const {
        if (!head) {
            cout << "Список пуст.\n";
            return;
        }

        Buyer* temp = head;
        cout << "Список покупок:\n";
        while (temp) {
            cout << temp->lastName << " " << temp->firstName
                << ", Карта: " << temp->cardNumber
                << ", Товар: " << temp->productName
                << ", Сумма: " << temp->purchaseAmount << " руб.\n";
            temp = temp->next;
        }
    }

    void print_total_by_buyer() const {
        if (!head) {
            cout << "Список пуст.\n";
            return;
        }

        Buyer* tempOuter = head;
        while (tempOuter) {
            bool alreadyPrinted = false;
            Buyer* check = head;
            while (check != tempOuter) {
                if (check->lastName == tempOuter->lastName && check->firstName == tempOuter->firstName) {
                    alreadyPrinted = true;
                    break;
                }
                check = check->next;
            }
            if (!alreadyPrinted) {
                double total = 0.0;
                Buyer* tempInner = head;
                while (tempInner) {
                    if (tempInner->lastName == tempOuter->lastName && tempInner->firstName == tempOuter->firstName) {
                        total += tempInner->purchaseAmount;
                    }
                    tempInner = tempInner->next;
                }
                cout << tempOuter->lastName << " " << tempOuter->firstName
                    << " - Суммарная стоимость покупок: " << total << " руб.\n";
            }
            tempOuter = tempOuter->next;
        }
    }

    ~BuyerList() {
        Buyer* current = head;
        while (current) {
            Buyer* next = current->next;
            delete current;
            current = next;
        }
    }
};

int main() {
    setlocale(LC_ALL, "Russian");

    BuyerList list;


    list.push_back("Bobrito", "Bandito", "12345", "Tomson", 50000);
    list.push_back("Bombordiro", "Crokodilo", "67890", "Bomb", 30000);
    list.push_back("Tralalela", "Tralala", "12345", "boots", 1500);
    list.push_back("Capushino", "Assasin", "11223", "Katana", 2500);
    list.push_back("Trilili", "Tralila", "12345", "Big boots", 12000);


    list.push_back("Bobrito", "Bandito", "12345", "Pylemet", 75000);
    list.push_back("Bobrito", "Bandito", "12345", "Mina", 20000);
    list.push_back("Tralalela", "Tralala", "12345", "Cross", 8000);
    list.push_back("Tralalela", "Tralala", "12345", "T-shorts", 1500);

    cout << "=== Все покупки ===\n";
    list.print_all();

    cout << "\n=== Суммарная стоимость покупок по каждому покупателю ===\n";
    list.print_total_by_buyer();

    return 0;
}