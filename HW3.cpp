#include<iostream>
using namespace std;

class student
{
public:
     int studentID ; 
     float studentGPA ; 
     string studentCourse ; 

             // Constructor 
    student(int sid, float sGPA, string sCourse) {
        studentID = sid;
        studentGPA = sGPA;
        studentCourse = sCourse;
    }
             // Default Constructor
    student() {
        studentID = 0;
        studentGPA = 0.0;
        studentCourse = "";
    }

             //SetFunctions
void set_studentID(){
cout << "Enter Your ID "<<endl;
}
void set_studentGPA(){
cout<<"Enter Your GPA" <<endl;
}
void set_studentCourse(){
cout<<"Enter The Course "<<endl;
}
              //GetFunctions 
int get_studentID(){
return studentID;
}              
float get_studentGPA(){
    return studentGPA;
}
string get_studentCourse(){
    return studentCourse;
}
};

class Node{
public:
student data ; 
Node*next ; 

              // Constructor 
    Node(student s) {
        data = s;
        next = NULL;
    }

};

class StudentQueue{
private:
    Node*front;
    Node*rear;
public:
    StudentQueue(){

        front = rear = NULL;
}

bool isEmpty()
{return (front == NULL);}

void Enqueue(student stu){
if(isEmpty()){
    Node*newNode = new Node(stu);
    front = rear = newNode;
}    
else  {
     Node*newNode = new Node(stu);
         rear->next = newNode;
         rear = newNode; 
   }  
}

void Dequeue(){
if(isEmpty()){

cout << " * The Queue Is Empty * " <<endl;

}
else if(front == rear){

   delete front;
   front = rear = NULL;

}
else  {

              Node*delptr = front ;
               front = front->next;
              delete delptr;
    }
} 

void Display(){
if(isEmpty()){
    cout<<" * Queue Is Empty * "<<endl;
}
else{

        Node*temp = front;
        while(temp != NULL ){

                    cout << "ID: "     << temp->data.get_studentID()
                     << " | GPA: " << temp->data.get_studentGPA()
                     << " | Course: " << temp->data.get_studentCourse()
                     << endl;     
                 temp = temp->next;
                    
             
    }

}

    
}

};

int main() {



    StudentQueue q;

    student s1(101, 3.5, "CS231");
    student s2(102, 3.8, "CS233");
    student s3(103, 4.1, "MH223");


    q.Enqueue(s1);
    q.Enqueue(s2);
    q.Enqueue(s3);
    q.Display();

    cout << "\n--- After Dequeue ---\n" << endl;

    q.Dequeue();
    q.Display();
 

 
 
    return 0;

}