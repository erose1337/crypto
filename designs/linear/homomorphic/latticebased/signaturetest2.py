# x ^ k mod P
# x ^ (s - k + r) == x ^ ((s + k + r) - k + r) == x ^ s

# signing_key = g^k
# e = H(signing_key || M)
# signature = k - (x + e)
# return signature, e

# verifier = g ^ signature + public_key ^ e
# e_v = H(verifier || M)
# assert e_v == e

from crypto.utilities import random_integer, big_prime, modular_inverse, modular_subtraction

A_SIZE = 32
B_SIZE = 32
X_SIZE = 32
P_SIZE = 33
PRIVATE_KEY_SIZE = 32

def generate_parameters(a_size=A_SIZE, b_size=B_SIZE,
                        x_size=X_SIZE, p_size=P_SIZE):
    a = random_integer(a_size)
    b = random_integer(b_size)
    x = random_integer(x_size)
    p = big_prime(p_size) 
    z = modular_inverse(modular_subtraction(1, a, p), p)
    return a, b, x, p, z
    
PARAMETERS = A, B, X, P, Z = generate_parameters()
        
def point_addition(x, a, b, p=P):  
    return ((a * x) + b) % p
           
def _sum_geometric_series(point_count, a=A, p=P, z=Z):
    t = modular_subtraction(1, a, p)
    return (t * z) % p  
    
def generate_a_b(point_count, a=A, p=P, z=Z):        
    _a = pow(a, point_count, p)   
    _b = _sum_geometric_series(point_count, _a, p, z)    
    return _a, _b
        
def generate_private_key(a=A, p=P, z=Z, private_key_size=PRIVATE_KEY_SIZE):
    point_count = random_integer(private_key_size)
    a, b = generate_a_b(point_count, a, p, z)
    return point_count, a, b            
        
def generate_public_key(private_key, parameters):   
    point_count, _a, _b = private_key    
    a, b, x, p, z = parameters
    public_key = point_addition(x, _a, _b, p)
    return public_key
    
def generate_keypair(private_key_size=PRIVATE_KEY_SIZE, parameters=PARAMETERS):
    a, b, x, p, z = parameters
    private_key = generate_private_key(a, p, z, private_key_size)
    public_key = generate_public_key(private_key, parameters)
    return public_key, private_key
    
def key_agreement(public_key, private_key, p=P):   
    point_count, _a, _b = private_key
    return point_addition(public_key, _a, _b, p)
    
def sign(m, x, p=P):
    r, priv_info = generate_keypair()    
    e = hash(r + m)
    k = priv_info[0]    
    s = modular_subtraction(k, (x[0] + e), p)
    return s, e

def verify(signature, M, y):
    s, e = signature
    sa, sb = generate_a_b(s)
    gs = point_addition(X, sa, sb)
    
    ea, eb = generate_a_b(e)
    ye = point_addition(y, ea, eb)
    
    rv = (gs + ye) % P
    ev = hash(rv + M)
    if ev == e:
        return True
    else:
        return False
        
def test_key_agreement():
    from unittesting import test_key_agreement
    test_key_agreement("keyagreement4", generate_keypair, key_agreement, iterations=10000)
    
def test_sign_verify():
    from unittesting import test_sign_verify
    test_sign_verify("signaturetest2", generate_keypair, sign, verify, iterations=10000)
    
if __name__ == "__main__":
    #test_key_agreement()
    test_sign_verify()
    