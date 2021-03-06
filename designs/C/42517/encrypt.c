#include "hash.c"

#define initialize_state(state, iv, key, extra_data, extra_data_size)({\
    hash_function(extra_data, extra_data_size, state);\
    for (index = 0; index < 8; index++){\
        state[index] ^= iv[index];\
        state[index + 8] = key[index];}\
    permutation(state);})
        
#define constant_time_comparison(flag, array1, array2, array_size, offset1, offset2)({\
    for (index = 0; index < array_size; index++){\
        flag = (state[index + offset1] ^ tag[index + offset2] ^ 0xFFFFFFFF) & flag;}})        
            
void encrypt(WORDSIZE* data, WORDSIZE* key, WORDSIZE* iv, WORDSIZE* extra_data, WORDSIZE* tag,
             unsigned long data_size, unsigned long extra_data_size){
    WORDSIZE state[16];
    unsigned long index;
    initialize_state(state, iv, key, extra_data, extra_data_size);
        
    unsigned long block_number;    
    for (block_number = 0; block_number < data_size / 8; block_number++){    
        copy(state, data, 8, 0, (block_number * 8));                       
        permutation(state);
        copy(data, state, 8, (block_number * 8), 0);}        
         
    for (index = 0; index < 8; index++){
        tag[index] = state[index + 8] ^ key[index];}}
        
int decrypt(WORDSIZE* data, WORDSIZE* key, WORDSIZE* iv, WORDSIZE* extra_data, WORDSIZE* tag,
             unsigned long data_size, unsigned long extra_data_size){
    WORDSIZE state[16];
    unsigned long index;
    for (index = 0; index < 8; index++){
        state[index + 8] = tag[index] ^ key[index];}
    
    unsigned long block_number = data_size / 8;    
    while (block_number-- > 0){        
        copy(state, data, 8, 0, (block_number * 8));               
        invert_permutation(state);
        copy(data, state, 8, (block_number * 8), 0);}        
            
    copy(tag, state, 8, 0, 8);          
    initialize_state(state, iv, key, extra_data, extra_data_size);  
    
    int valid = 0xFFFFFFFF;
    constant_time_comparison(valid, state, tag, 8, 8, 0);
    return valid;}    
        
void test_encrypt_decrypt(){
    WORDSIZE data[8], key[8], iv[8], extra_data[8], tag[8];
    unsigned long index;
    
    for (index = 0; index < 8; index++){
        data[index] = 0;
        key[index] = 0;
        iv[index] = 0;
        extra_data[index] = 0;}
    data[0] = 1;
    key[0] = 1;
    iv[0] = 1;
    extra_data[0] = 1;
    
    encrypt(data, key, iv, extra_data, tag, 8, 8);  
    //iv[0] = 0;    
    //tag[0] = 0;
    //extra_data[0] = 0;
    if (decrypt(data, key, iv, extra_data, tag, 8, 8) == 0xFFFFFFFF){
        printf("%lu%lu%lu%lu%lu%lu%lu%lu\n", data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]);}
    else{
        printf("Decryption failed\n");}}
    
void test_encrypt_time(){    
	WORDSIZE message[8], key[8], iv[8], extra_data[8], tag[8];
    unsigned long index;
    for (index = 0; index < 8; index++){
        message[index] = 1;}
    printf("Encrypting and authenticating 3,000,000 256-bit blocks (~91MB)\n");
    clock_t begin = clock();
    for (index = 0; index < 3000000; index++){
        encrypt(message, key, iv, extra_data, tag, 8, 8);}
    clock_t end = clock();
    
    double time_spent = (double)(end - begin) / CLOCKS_PER_SEC;    
    printf("Time required: %.2fs\n", time_spent);
    printf("%lu%lu%lu%lu%lu%lu%lu%lu\n", message[0], message[1], message[2], message[3], message[4], message[5], message[6], message[7]);}
    
int main(){
    test_encrypt_decrypt();
    test_encrypt_time();
    return 0;}
    