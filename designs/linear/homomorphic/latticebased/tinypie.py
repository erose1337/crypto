from crypto.utilities import random_integer, modular_inverse, big_prime

P = big_prime(50)

def calculate_parameter_sizes(security_level):
    """ usage: calculate_parameters_sizes(security_level) => short_inverse size, r size, s size, e size, P size
    
        Given a target security level, designated in bytes, return appropriate parameter sizes for instantiating the trapdoor. """
    short_inverse_size = (security_level * 2) + 1
    p_size = short_inverse_size + security_level + 1
    return short_inverse_size, security_level, security_level, security_level, p_size
    
def generate_private_key(short_inverse_size=24, p=P):
    """ usage: generate_private_key(short_inverse_size=65, p=P) => private_key
    
        Returns 1 integer, suitable for use as a private key. """
    short_inverse = random_integer(short_inverse_size)       
    a = modular_inverse(short_inverse, p)
    b = random_integer(11)
    c = random_integer(11)    
    return short_inverse, a, b, c
    
def generate_public_key(private_key, p=P): 
    """ usage: generate_public_key(private_key, p=P) => public_key
    
        Returns 1 integer, suitable for use as a public key. """
    ai, a, b, c = private_key
    public_key = ((a * b) + c) % p    
    return public_key
        
def generate_keypair():
    """ usage: generate_keypair() => public_key, private_key
    
        Generate a keypair; Returns 2 integers. """
    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    return public_key, private_key
    
def exchange_key(public_key, s_size=13, e_size=25, p=P): 
    """ usage: exchange_key(public_key, s_size=32, e_size=32, p=P) => ciphertext, secret
    
        Returns a ciphertext and a shared secret.
        The ciphertext should be delivered to the holder of the associated private key, so that they may recover the shared secret. """
    s = random_integer(s_size)  
    ciphertext = (public_key * s) + random_integer(e_size)
    return ciphertext % p, s
    
def recover_key(ciphertext, private_key, p=P):
    """ usage: recover_key(ciphertext, private_key, p=P) => secret
    
        Returns a shared secret in the form of a random integer. """
    # s(ab + c) + e
    # sab + sc + e
    # sb + aisc + aie
    # sb + ai(cs + e)    # 32 + 32    65 + 64 + 1 
    #                    # 16 + 32    49 + 64 + 1     114
    #                    # 17 + 7     24 + 24 + 1      49
    ai, a, b, c = private_key
    rb_aicr_e = (ai * ciphertext) % p
    rb = rb_aicr_e % ai
    return rb / b    
    
# c = m * x mod P
# c = c mod x
# c = c / y

def hash_public_key(hash_function, public_key):
    """ usage: hash_public_key(hash_function, public_key) => public_key_fingerprint
    
        Returns a hash of public key, suitable for use as an identifier. """
    return hash_function(serialize_public_key(public_key))
        
def serialize_public_key(public_key):
    """ usage: serialize_public_key(public_key) => serialized_public_key
        
        Returns a saved public key, in the form of bytes. """
    return save_data(public_key)
    
def deserialize_public_key(serialized_public_key):
    """ usage: deserialize_public_key(serialized_public_key) => public_key
        
        Loads a saved public key, as produced by serialize_public_key. """
    return load_data(serialized_public_key)
    
def test_serialized_public_key_deserialize_public_key():
    public_key, _ = generate_keypair()
    serialized = serialize_public_key(public_key)
    _public_key = deserialize_public_key(serialized)
    assert _public_key == public_key, (_public_key, public_key)
    
def test_exchange_key_recover_key():
    from unittesting import test_key_exchange
    test_key_exchange("epqcryptokeyexchange", generate_keypair, exchange_key, recover_key, iterations=10000)
    
if __name__ == "__main__":
    test_exchange_key_recover_key()
           