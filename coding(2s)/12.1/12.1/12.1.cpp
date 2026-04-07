#include <iostream>
using namespace std;

struct Node {
    int data;
    Node* next;

    Node(int value) : data(value), next(nullptr) {}
};

class MyList {
private:
    Node* head; 

public:
    MyList() : head(nullptr) {}


    void push_back(int value) {
        Node* newNode = new Node(value);
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

  
    void delete_last() {
        if (!head) {
            cout << "Список пуст.\n";
            return;
        }
        if (!head->next) { 
            delete head;
            head = nullptr;
            cout << "Последний элемент удалён. Список теперь пуст.\n";
            return;
        }

        Node* temp = head;
        while (temp->next->next) { 
            temp = temp->next;
        }
        delete temp->next; 
        temp->next = nullptr;
        cout << "Последний элемент успешно удалён.\n";
    }

    void print() const {
        if (!head) {
            cout << "Список пуст.\n";
            return;
        }

        Node* temp = head;
        cout << "Список: ";
        while (temp) {
            cout << temp->data << " -> ";
            temp = temp->next;
        }
        cout << "nullptr\n";
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
    list.push_back(10);
    cout << "Исходный список:\n";
    list.print();

    list.delete_last();

    cout << "Список после удаления последнего элемента:\n";
    list.print();

    return 0;
}