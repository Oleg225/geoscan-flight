#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Структура для хранения данных о покупателе
typedef struct {
    char surname[50];
    char name[50];
    int card_number;
    char product_name[50];
    float purchase_price;
} Customer;

// Узел односвязного списка
typedef struct Node {
    Customer data;
    struct Node* next;
} Node;

// Функция для создания нового узла
Node* create_node(Customer customer) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    if (new_node == NULL) {
        printf("Ошибка выделения памяти\n");
        exit(1);
    }
    new_node->data = customer;
    new_node->next = NULL;
    return new_node;
}

// Функция для добавления элемента в конец списка
void append(Node** head, Customer customer) {
    Node* new_node = create_node(customer);

    if (*head == NULL) {
        *head = new_node;
        return;
    }

    Node* last = *head;
    while (last->next != NULL) {
        last = last->next;
    }

    last->next = new_node;
}

// Функция для удаления элемента по индексу
void delete_at(Node** head, int index) {
    if (*head == NULL) {
        printf("Список пуст\n");
        return;
    }

    Node* temp = *head;

    // Если удаляем первый элемент
    if (index == 0) {
        *head = temp->next;
        free(temp);
        return;
    }

    // Находим предыдущий элемент перед удаляемым
    for (int i = 0; temp != NULL && i < index - 1; i++) {
        temp = temp->next;
    }

    // Если индекс выходит за пределы списка
    if (temp == NULL || temp->next == NULL) {
        printf("Индекс выходит за пределы списка\n");
        return;
    }

    // Удаляем узел
    Node* next = temp->next->next;
    free(temp->next);
    temp->next = next;
}

// Функция для вывода списка на экран
void print_list(Node* head) {
    printf("Список покупателей:\n");
    printf("----------------------------------------------------------------------------------------\n");
    printf("| Фамилия | Имя | Номер карты | Наименование товара | Стоимость покупки |\n");
    printf("----------------------------------------------------------------------------------------\n");

    Node* current = head;
    while (current != NULL) {
        printf("| %-8s | %-4s | %-11d | %-19s | %-17.2f |\n",
            current->data.surname,
            current->data.name,
            current->data.card_number,
            current->data.product_name,
            current->data.purchase_price);
        current = current->next;
    }
    printf("----------------------------------------------------------------------------------------\n");
}

// Функция для вывода суммарной стоимости покупок каждого покупателя
void print_purchase_totals(Node* head) {
    printf("Суммарная стоимость покупок по покупателям:\n");
    printf("--------------------------------------------\n");
    printf("| Фамилия | Имя | Общая стоимость |\n");
    printf("--------------------------------------------\n");

    Node* current = head;
    while (current != NULL) {
        // Считаем сумму для текущего покупателя
        float total = current->data.purchase_price;
        Node* inner = current->next;
        Node* prev = current;

        // Проверяем остальные записи на совпадение имени и фамилии
        while (inner != NULL) {
            if (strcmp(current->data.surname, inner->data.surname) == 0 &&
                strcmp(current->data.name, inner->data.name) == 0) {
                total += inner->data.purchase_price;

                // Удаляем дубликат из списка, чтобы не обрабатывать его снова
                Node* to_delete = inner;
                prev->next = inner->next;
                inner = inner->next;
                free(to_delete);
            }
            else {
                prev = inner;
                inner = inner->next;
            }
        }

        printf("| %-8s | %-4s | %-15.2f |\n",
            current->data.surname,
            current->data.name,
            total);

        current = current->next;
    }
    printf("--------------------------------------------\n");
}

// Функция для сохранения списка в бинарный файл
void save_to_file(Node* head, const char* filename) {
    FILE* file = fopen(filename, "wb");
    if (file == NULL) {
        printf("Ошибка открытия файла для записи\n");
        return;
    }

    Node* current = head;
    while (current != NULL) {
        fwrite(&(current->data), sizeof(Customer), 1, file);
        current = current->next;
    }

    fclose(file);
    printf("Данные успешно сохранены в файл '%s'\n", filename);
}

// Функция для загрузки списка из бинарного файла
Node* load_from_file(const char* filename) {
    FILE* file = fopen(filename, "rb");
    if (file == NULL) {
        printf("Ошибка открытия файла для чтения\n");
        return NULL;
    }

    Node* head = NULL;
    Customer customer;

    while (fread(&customer, sizeof(Customer), 1, file) == 1) {
        append(&head, customer);
    }

    fclose(file);
    printf("Данные успешно загружены из файла '%s'\n", filename);
    return head;
}

// Функция для освобождения памяти списка
void free_list(Node* head) {
    Node* current = head;
    while (current != NULL) {
        Node* next = current->next;
        free(current);
        current = next;
    }
}

// Функция для ввода данных о покупателе с клавиатуры
Customer input_customer() {
    Customer customer;

    printf("Введите фамилию покупателя: ");
    scanf("%s", customer.surname);

    printf("Введите имя покупателя: ");
    scanf("%s", customer.name);

    printf("Введите номер карты: ");
    scanf("%d", &customer.card_number);

    printf("Введите наименование товара: ");
    scanf("%s", customer.product_name);

    printf("Введите стоимость покупки: ");
    scanf("%f", &customer.purchase_price);

    return customer;
}

// Основное меню программы
void menu() {
    Node* head = NULL;
    char filename[100] = "customers.dat";
    int choice;

    do {
        printf("\nМеню:\n");
        printf("1. Добавить покупателя\n");
        printf("2. Удалить покупателя по индексу\n");
        printf("3. Вывести список покупателей\n");
        printf("4. Загрузить данные из файла\n");
        printf("5. Сохранить данные в файл\n");
        printf("6. Вывести суммарную стоимость покупок по покупателям\n");
        printf("0. Выход\n");
        printf("Выберите действие: ");
        scanf("%d", &choice);

        switch (choice) {
        case 1: {
            Customer customer = input_customer();
            append(&head, customer);
            printf("Покупатель добавлен\n");
            break;
        }
        case 2: {
            int index;
            printf("Введите индекс для удаления: ");
            scanf("%d", &index);
            delete_at(&head, index);
            printf("Покупатель удален\n");
            break;
        }
        case 3:
            print_list(head);
            break;
        case 4:
            free_list(head);
            head = load_from_file(filename);
            break;
        case 5:
            save_to_file(head, filename);
            break;
        case 6:
            print_purchase_totals(head);
            break;
        case 0:
            free_list(head);
            printf("Программа завершена\n");
            break;
        default:
            printf("Неверный выбор\n");
        }
    } while (choice != 0);
}

int main() {
    menu();
    return 0;
}