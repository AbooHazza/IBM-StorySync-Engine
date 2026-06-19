#include <iostream>
using namespace std;

class student {
public : 
float studentgpa ; 
int studentid ; 
string studentcourse ;

student(int ID , float GPA , string course)
{
studentcourse = course ; 
studentgpa = GPA ; 
studentid = ID ; 
}

student()
{
    studentcourse = " " ; 
    studentgpa = 0.0 ;
    studentid = 0 ; 
}

};

class Node{
    public:
    student data ; 
    Node*next ; 

};

class stacks{
private:
Node*top ; 

public:
stacks(){
    top = NULL;
}

bool isEmpty()
{return top == NULL;}

void push(student s){
    Node*newNode = new Node;
    newNode->data = s;
    newNode->next = top ; 
    top = newNode ; 
}

void pop(){
    if(isEmpty()){
        cout<<"Stack is Empty !"<<endl;
    }
else{
    Node*temp = top;
    top = top->next;
    delete temp;
}
}

~stacks(){
    if(!isEmpty){
        pop();
    }
}

};

//                   |||===========================================|||
//                ===|||     Student class withstack & linked list |||===
//                   |||===========================================|||

int main(){





}