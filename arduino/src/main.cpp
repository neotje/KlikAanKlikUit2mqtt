#include <Arduino.h>
#include <kk.h>
#include <SoftwareSerial.h>

//SoftwareSerial SUART(2,3);
HardwareSerial &SUART = Serial;

#define OFF "OFF"
#define ON "ON"
#define DIM "DIM"

void setup()
{
  SUART.begin(9600);

  kk_init();
}

char *parse(char **s)
{
  char *p = *s;
  char *q;
  while (*p == ' ')
    p++;
  q = p;
  while ((*p != ' ') && (*p != 0))
    p++;
  if (*p == ' ')
    *p++ = 0;
  *s = p;
  return q;
}

void loop()
{
  unsigned long address;
  unsigned char unit, dimlevel, onoff;
  static char inbuf[20];
  static unsigned char i = 0;
  char *p, *s, c;
  if (kk_available())
  {
    kk_receive(&address, &unit, &onoff, &dimlevel);
    SUART.print("{ \"A\": \"");
    SUART.print(address);
    SUART.print("\", \"U\": ");
    SUART.print(unit);
    SUART.print(", \"C\": \"");
    SUART.print((onoff == 0) ? OFF : (onoff == 1) ? ON
                                                    : DIM);
    SUART.print("\", \"D\": \"");
    SUART.print(dimlevel);
    SUART.println("\"}");
  }
  if (SUART.available())
  {
    c = SUART.read();
    if (c == '\n' || c == '\r')
    {
      inbuf[i++] = 0;
      i = 0;
      //SUART.println(inbuf);
      p = inbuf;
      if (strlen(p) > 5)
      {
        s = parse(&p);
        address = atol(s);
        s = parse(&p);
        unit = atoi(s);
        s = parse(&p);
        onoff = 0;
        if (strcmp(s, OFF) == 0)
          onoff = 0;
        else if (strcmp(s, ON) == 0)
          onoff = 1;
        else if (strcmp(s, DIM) == 0)
          onoff = 2;
        if (onoff == 2)
        {
          s = parse(&p);
          dimlevel = atoi(s);
        }
        else
          dimlevel = 0;
        SUART.print("{ \"A\": \"");
        SUART.print(address);
        SUART.print("\", \"U\": ");
        SUART.print(unit);
        SUART.print(", \"C\": \"");
        SUART.print((onoff == 0) ? OFF : (onoff == 1) ? ON
                                                        : DIM);
        SUART.print("\", \"D\": \"");
        SUART.print(dimlevel);
        SUART.println("\"}");
        kk_send(address, unit, onoff, dimlevel);
      }
    }
    if ((i < 19) && (c != 13))
    {
      inbuf[i++] = c;
    }
  }
}