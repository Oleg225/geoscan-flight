#include <iostream>
#include <string>
using namespace std;

struct Node {
    string lastName;
    int age;
    Node* next;

    Node(const string& name, int a) : lastName(name), age(a), next(nullptr) {}
};

class MyList {
private:
    Node* head;

public:
    MyList() : head(nullptr) {}


    void push_back(const string& name, int age) {
        Node* newNode = new Node(name, age);
        if (!head) {
            head = newNode;
        }
        else {
            Node* temp = head;
            while (temp->next) {
                temp = temp->next;
            }
            temp->next = newNode;
        }
    }


    void search_by_lastname(const string& name) const {
        Node* temp = head;
        int count = 0;
        cout << "Результаты поиска по фамилии \"" << name << "\":\n";
        while (temp) {
            if (temp->lastName == name) {
                cout << "- " << temp->lastName << ", возраст: " << temp->age << endl;
                count++;
            }
            temp = temp->next;
        }
        if (count == 0) {
            cout << "Студенты с такой фамилией не найдены.\n";
        }
        else {
            cout << "Всего найдено: " << count << endl;
        }
    }


    void search_by_age(int age) const {
        Node* temp = head;
        int count = 0;
        cout << "Результаты поиска по возрасту " << age << ":\n";
        while (temp) {
            if (temp->age == age) {
                cout << "- " << temp->lastName << ", возраст: " << temp->age << endl;
                count++;
            }
            temp = temp->next;
        }
        if (count == 0) {
            cout << "Студенты с таким возрастом не найдены.\n";
        }
        else {
            cout << "Всего найдено: " << count << endl;
        }
    }


    void print() const {
        if (!head) {
            cout << "Список пуст.\n";
            return;
        }
        cout << "Список студентов:\n";
        Node* temp = head;
        while (temp) {
            cout << temp->lastName << ", возраст: " << temp->age << endl;
            temp = temp->next;
        }
    }


    ~MyList() {
        Node* current = head;
        while (current) {
            Node* next = current->next;
            delete current;
            current = next;
        }
    }
};

int main() {
    setlocale(LC_ALL, "Russian");

    MyList list;

    list.push_back("Ivanov", 20);
    list.push_back("Petrov", 22);
    list.push_back("Yakovlev", 19);
    list.push_back("Ivanov", 21);

    list.print();

    int choice;
    cout << "\nВыберите тип поиска:\n";
    cout << "1 - По фамилии\n";
    cout << "2 - По возрасту\n";
    cout << "Ваш выбор: ";
    cin >> choice;

    if (choice == 1) {
        string name;
        cout << "Введите фамилию для поиска: ";
        cin >> name;
        list.search_by_lastname(name);
    }
    else if (choice == 2) {
        int age;
        cout << "Введите возраст для поиска: ";
        cin >> age;
        list.search_by_age(age);
    }
    else {
        cout << "Неверный выбор.\n";
    }

    return 0;
}