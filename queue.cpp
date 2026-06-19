#include <iostream>
using namespace std;





                    //          --------------------
                    //-> front   |  |  |  |  |  |  |  <- rear        FIFO (First in first out)
                    //          --------------------


class Node{

public:
int data ;
Node*next ;

Node(int value)
{
    data = value ;
    next = nullptr ;
}
};

class Queue{

    private:
    Node*front ; 
    Node*rear ;
     
    public:                     

    Queue()                    
    {                                  
        front,rear = nullptr;
    }


    bool isEmpty(){
    return (front = NULL);
    }
    
    void enqueue(int item ){
                  
        Node*newNode = new Node(item);


        if(isEmpty())
        {
          front = rear = newNode;
        }
        else{

           rear->next = newNode ; 
           rear = newNode ; 
        }
    }

    void dequeue(){

        if (isEmpty()){

            cout<<"The Queue is Empty"<<endl;
        }
        else if(front = rear){
            
            delete front ;
            front = rear = NULL ;

        }
          else{

         Node*delptr = front ;
         front = front->next;
         delete delptr;
          }     


    }


    








};





int main(){



}