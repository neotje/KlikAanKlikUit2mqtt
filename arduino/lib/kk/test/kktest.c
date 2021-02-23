#include<stddef.h>
#include<stdio.h>
#include "../kk.h"

#define HIGH 0x1
#define LOW  0x0

#define INPUT 0x0
#define OUTPUT 0x1

extern void digitalWrite(int pin,int data);
extern int digitalRead(int pin);
extern void PinMode(int pin, int mode);

unsigned char ddd[50000];
int           nnn=0;
int           rrr=0;
int           pinmode[20];

void cli(void)
  {
  }
void sei(void)
  {
  }
  
void pinMode(int pin,int mode)
  {
    pinmode[pin]=mode;
  }

void digitalWrite(int pin,int data)
  {
    if (pinmode[pin]==INPUT)
      printf("ERROR in DigitalWrite : pin %d has inputmode",pin);
    if (pin==KK_TXPIN)
      {
       printf("%d",data);
       ddd[nnn++]=data;
      }
    else
      printf("%c",data?'S':'R');
  }
int digitalRead(int pin)
  {
    int data;    
    if (pinmode[pin]==OUTPUT)
      printf("ERROR in DigitalRead : pin %d has output mode",pin);
    if (rrr<nnn)
      {
        data=ddd[rrr++];
      } 
    else       
       data=0;;
    printf("%d",data);
    return(data);   
  }


 
void main()
  {
    FILE *f=NULL; 	
    char c;
    unsigned long address;
    unsigned char unit,dimlevel,onoff;
    int i,j, item, lastnnn;
    unsigned long addrlist[10] = {3,4,5,4, 2454,2455,2456,2457,3, 1010};
    unsigned char unitlist[10] = {2,2,2,12,5,   6,   6,   6,   7, 255};
    unsigned char cmdlist[10]  = {1,0,0,1, 0,   1,   2,   2,   1, 0};
    unsigned char dimlist[10]  = {0,0,0,0, 0,   0,  12,   13,  0, 0};
    kk_init();
    printf("start \n");
    /* send first 5 items */
    for (item=0;item<5;item++)
      {
        while (kk_sendbuffull())
          kk_statehandler();
        kk_send(addrlist[item],unitlist[item],cmdlist[item],dimlist[item]);
      } 
    /* pause sending, receive a few frames but stop in the middle */   
    printf("\npause sending \n"); 
    while (!kk_sendbufempty())
      kk_statehandler();
    printf("\npause sending \n"); 
    /* wait until we are done sending */
    while(pinmode[KK_RXPIN]==OUTPUT)
      kk_statehandler();
    /* a few more */
    for (i=0;i<10;i++)  
      kk_statehandler();
    printf("\nresume sending \n");      
    /* send the rest */  	
    for (item=5;item<10;item++)
      {
        while (kk_sendbuffull())
          kk_statehandler();
        kk_send(addrlist[item],unitlist[item],cmdlist[item],dimlist[item]);
      } 
    while(pinmode[KK_RXPIN]==INPUT)
      kk_statehandler();
    printf("\nresumed sending \n");
    /* send all */
    for (i=0;i<3;i++)  
      kk_statehandler();
    lastnnn=0;
    while (nnn>lastnnn)
      {
        lastnnn=nnn;
        kk_statehandler();
      }  
    printf("\nfinished sending \n");
        
    
    
    /* receive all*/  
    item = 0;

 
    while(rrr!=nnn)
      {
          kk_statehandler();
          if (kk_available())
            {
               kk_receive(&address,&unit,&onoff,&dimlevel);
               printf("A: %8.8lx U: %2.2x %3s %3.3d\n",address,unit,(onoff==0)?"Off":(onoff==1)?"On":"Dim",dimlevel);
               if (  (address  != addrlist[item])
                   ||(unit     != unitlist[item])
                   ||(onoff    != cmdlist[item])
                   ||(dimlevel != dimlist[item]))
               {
               	  printf("ERROR: compare error, item %d\n",item);
               }    
               item++;
            }
      }    
    printf("done receiving \n");
  }
  