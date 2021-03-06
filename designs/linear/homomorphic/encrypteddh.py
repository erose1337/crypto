from math import log

from crypto.utilities import random_integer, modular_inverse, big_prime

SECURITY_LEVEL = 32

def generate_parameters(security_level=SECURITY_LEVEL):
    k_size = security_level
    
    # best quantum attack against knapsacks is slightly less then O(.25N)
    # where N = number of elements summed together 
    # N should be half of the entire set    
    knapsack_multiplier = 4                                          
    knapsack_size = 8 * security_level * 4 * 2                   
    assert knapsack_size == 2048, knapsack_size
    subset_count = knapsack_size / 2
    assert subset_count == 1024, subset_count
    knapsack_element_size = knapsack_size / 8  # (knapsack_element_size in bytes)
    assert knapsack_element_size == 256, knapsack_element_size
    
    share_size = security_level    
    p_size = knapsack_element_size
    generator = 3
    
    parameters = {"k_size" : k_size,
                  "knapsack_size" : knapsack_size, "knapsack_element_size" : knapsack_element_size,
                  "subset_count" : subset_count, "share_size" : share_size,
                  "p_size" : p_size, "generator" : generator}
    return parameters
    
def find_p(parameters):
    from crypto.utilities import is_prime
    p_size = parameters["p_size"]
    p = 2 ** ((p_size * 8) + 1)    
    offset = 1
    while not is_prime(p + offset):
        offset += 2
    return p, offset
    
PARAMETERS = generate_parameters(SECURITY_LEVEL)      
#P_BASE, OFFSET = find_p(PARAMETERS)
#print OFFSET
#P = P_BASE + OFFSET    
P = (2 ** ((PARAMETERS["p_size"] * 8) + 1)) + 227
PARAMETERS["p"] = P

def secret_split(m, security_level, shares, modulus):
    shares = [random_integer(security_level) for count in range(shares - 1)]
    shares_product = reduce(lambda x, y: (x * y) % modulus, shares)
    remaining_share = (modular_inverse(shares_product, modulus) * m) % modulus
    shares.append(remaining_share)
    return shares
    
def generate_key(parameters=PARAMETERS):
    k_size = parameters["k_size"]
    p = parameters['p']
    while True:
        k1 = random_integer(k_size)
        k2 = random_integer(k_size)
        try:
            k1i = modular_inverse(k1, p - 1)
            k2i = modular_inverse(k2, p - 1)
        except ValueError:
            continue
        else:
            break
    return (k1, k2), (k1i, k2i)
    
def private_key_encrypt(m, key, parameters=PARAMETERS):
    p = parameters['p']
    x, y = secret_split(m, parameters["share_size"], 2, p)
    k1, k2 = key[0]
    return pow(x, k1, p), pow(y, k2, p)
    
def private_key_decrypt(ciphertext, key, parameters=PARAMETERS):    
    p = parameters['p']
    c1, c2 = ciphertext
    k1i, k2i = key[1]    
    return (pow(c1, k1i, p) * pow(c2, k2i, p)) % p
    
def multiply(c1, c2, p=P):
    return [(c1[index] * c2[index]) % p for index in range(len(c1))]
    
def scalar_exponentiation(ciphertext, exponent, p=P):
    return [pow(element, exponent, p) for element in ciphertext]
    
def generate_private_key(parameters=PARAMETERS):
    return generate_key(parameters)
    
def generate_public_key(private_key, parameters=PARAMETERS):
    generator_ciphertext = private_key_encrypt(parameters["generator"], private_key, parameters)
    public_key = generator_ciphertext, []
    for element_number in range(parameters["knapsack_size"]):
        ciphertext = private_key_encrypt(1, private_key, parameters)
        public_key[1].append(ciphertext)
    return public_key
    
def generate_keypair(parameters=PARAMETERS):    
    private_key = generate_private_key(parameters)
    public_key = generate_public_key(private_key, parameters)
    return public_key, private_key
    
def random_element(set_size):       
    set_size_bits = int(log(set_size, 2))
    integer_size_bytes = int((set_size_bits / 8) + 1)
    return random_integer(integer_size_bytes) % (2 ** set_size_bits)
    
def encapsulate_key(public_key, parameters=PARAMETERS):
    x = random_integer(parameters["k_size"])
    p = parameters["p"]
    shared_secret = pow(parameters["generator"], x, p)
    ciphertext = scalar_exponentiation(public_key[0], x, p)
    
    knapsack_size = parameters["knapsack_size"]
    for count in range(parameters["subset_count"]):
        encryption_of_1 = public_key[1][random_element(knapsack_size)]
        ciphertext = multiply(ciphertext, encryption_of_1, p)
    return ciphertext, shared_secret
    
def recover_key(ciphertext, private_key, parameters=PARAMETERS):
    return private_key_decrypt(ciphertext, private_key, parameters)    
        
def test_encapsulate_key():
    from crypto.designs.linear.homomorphic.latticebased.unittesting import test_key_exchange
    test_key_exchange("encrypted DH", generate_keypair, encapsulate_key, recover_key, iterations=10)       
    
if __name__ == "__main__":
    test_encapsulate_key()
    