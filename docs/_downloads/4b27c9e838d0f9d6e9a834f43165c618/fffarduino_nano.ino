#define ROW_PORT PORTB
#define ROW_DDR DDRB
#define COL_PORT PORTC
#define COL_DDR DDRC
#define MOD_PORT PORTD
#define MOD_DDR DDRD
#define PX_VAL PC5
#define SET_PX PD2

#define DELAY 150

#define BUFFERSIZE 126*13/7 // number of bytes for buffer
byte buffer[BUFFERSIZE];
byte old_buffer[BUFFERSIZE];
byte width = 28;
byte height = 13;

void setup() {
  /*
   * configuration of output pins on arduino nano
   */
  ROW_DDR |= 0b00011111;  // PB0 - PB4 output: address of rows
                          // Arduino: D8 - D12
  COL_DDR |= 0b00111111;  // PC0 - PC5 output: address of cols, 
                          // PC5 is the inverse pixel value 
                          // (PC5 = 1 for black and PC5 = 0 for yellow pixel)
                          // Arduino: A0 - A5
  MOD_DDR |= 0b11111100;  // PD2 - PD7 output: PD2 = 1 to set flip or flop a pixel, 
                          // PD3 - PD7: modul selection 
                          // Arduino: D2 - D7

  Serial.begin(9600);
}

void flipdot(int x, int y, int val) {
  /*  
   * Immediately flip the dot at (x|y) to the given value.
   *   
   * Adressierung der Zeilen und Spalten:
   *  - für die Adressierung werden jeweils 5 Bit verwendet
   *  - mit den niederen 3 Bit lassen sich 7 Zeilen/Spalten adressieren, wobei 0b000 keine
   *    Zeile oder Spalte adressiert. Die erste Zeile wird also mit 0b001 und die 7. Zeile mit
   *    0b111 adressiert.
   *  - mit den anderen beiden Bits wird die Zeilen- oder Spaltenadresse erhöht
   *  - Beispiel: 0b00111 = Adresse der siebten Zeile/Spalte
   *  - Beispiel: 0b01001 = Adresse der achten Zeile/Spalte
   *  - Beispiel: 0b01111 = Adresse der vierzehnten Zeile/Spalte
   *  - Beispiel: 0b11111 = Adresse der achtundzwanzigsten Zeile/Spalte
   * Eine anzeige kann aus mehreren Modulen bestehen. Die Modulnummer gibt an, auf welchem
   * Modul sich der Pixel befindet. Ein Modul hat 28 Spalten.
   */
  int mod = x / 28;                 // module number
  int col = x % 28;                 // column of current module
  int row_addr = y / 7 << 3;        // most significant two bits of row address
  row_addr += y % 7 + 1;            // least significant three bits of row address
  int col_addr = col / 7 << 3;      // most significant two bits of row address
  col_addr += col % 7 + 1;          // least significant three bits of row address
  if(val == 0) {
    col_addr |= (1<<PX_VAL);  // PD5 = 1 for black pixel
  }
  else {
    col_addr &= ~(1<<PX_VAL); // PD5 = 0 for yellow pixel
  }
  ROW_PORT = row_addr;
  COL_PORT = col_addr;
  MOD_PORT |= (1<<SET_PX) | (1<<(mod+3));
  delayMicroseconds(DELAY);
  if(val == 1) delayMicroseconds(DELAY);    // yellow pixels require more time than black ones
  MOD_PORT &= ~((1<<SET_PX) | (1<<(mod+3)));
}

void show() {
  /*
   * Show the current buffer on the flip dot display.
   */
  int used_buffer_size = width * height / 7;
  for(int i = 0; i < used_buffer_size; i++) {
    if(buffer != old_buffer) {
      for(int j = 0; j < 7; j++) {
        if( ((1<<j) & buffer[i]) != ((1<<j) & old_buffer[i]) ) {
          int x = (i*7 + 6 - j) % width;
          int y = (i*7 + 6 - j) / width;
          int val = (1<<j) & buffer[i];
          flipdot(x, y, val);
        }
      }
      old_buffer[i] = buffer[i];
    }
  }
}

void serialEcho() {
  byte localBuffer[1];
  Serial.readBytes(localBuffer, 1);
  Serial.print(localBuffer[0], DEC);
}

void pxSet(byte val) {
  byte localBuffer[2];
  Serial.readBytes(localBuffer, 2);
  int x = localBuffer[0];
  int y = localBuffer[1];
  int byte_in_buffer = (y * width / 7) + (x / 7);
  int bit_in_bufferbyte = x % 7;
  if(val == 0) {
    buffer[byte_in_buffer] &= ~(1<<(6-bit_in_bufferbyte));
  }
  else {
    buffer[byte_in_buffer] |= (1<<(6-bit_in_bufferbyte));
  }
  // flipdot(x, y, val); 
  show();
}

void picture() {
  int used_buffer_size = width * height / 7;
  Serial.readBytes(buffer, used_buffer_size);
  show();
}

void setupDimension() {
  byte localBuffer[2];
  Serial.readBytes(localBuffer, 2);
  width = localBuffer[0];
  height = localBuffer[1];
}

void loop() {
  if(Serial.available() > 0) {
    int input = Serial.read();
    if(input == 0b11110000) {
      serialEcho();
    }
    if(input == 0b10000011) {
      pxSet(1);
    }
    if(input == 0b10000010) {
      pxSet(0);
    }
    if(input == 0b10000001) {
      picture();
    }
    if(input == 0b10010000) {
      setupDimension();
    }
  }
}
