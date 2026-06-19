#include <iostream>
using namespace std;


class Node{

public:
int data;
Node*next;


Node(int value)
{
    data = value;
    next = nullptr;
}
};

class Stack{

    private:

    Node*top;

    public:

    Stack(){

top = nullptr;

    }


    bool isEmpty(){

           return {top == NULL};
    }
    
    void push(int item)
    {
     if(isEmpty())
     {

        Node*newNode = new Node(item);
        newNode->next = NULL;
        top = newNode ;

     }
     else
     {

    Node*newNode = new Node(item);
    newNode->next = top;
    top = newNode;

     }
    }

int pop(){

    if(isEmpty()){

cout<<"Stack is Empty"<<endl;


    }
    else
    {
    int item ;
     Node*delptr = top;
     item = top->data;
     top = top->next;
     delete delptr;
     return item;
    }


}


};



int main(){





}