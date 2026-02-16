import random
from .SHA_256 import sha256_hash  # Your pure Python SHA256

# ==========================================
# Curve Parameters (secp256k1)
# ==========================================

p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
a = 0
b = 7

G = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
)

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# ==========================================
# Utility Functions
# ==========================================

def inverse_mod(k, mod):
    return pow(k % mod, -1, mod)

def is_on_curve(P):
    if P is None:
        return True
    x, y = P
    return (y * y - (x * x * x + a * x + b)) % p == 0

def point_add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P

    x1, y1 = P
    x2, y2 = Q

    if x1 == x2 and (y1 + y2) % p == 0:
        return None

    if P == Q:
        if y1 == 0:
            return None
        m = (3 * x1 * x1 + a) * inverse_mod((2 * y1) % p, p)
    else:
        m = (y2 - y1) * inverse_mod((x2 - x1) % p, p)

    m %= p
    x3 = (m * m - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return (x3, y3)

def scalar_mult(k, P):
    result = None
    addend = P

    while k > 0:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1

    assert is_on_curve(result)
    return result

# ==========================================
# Key Generation
# ==========================================

def generate_keys():
    private_key = random.randrange(1, n)
    public_key = scalar_mult(private_key, G)
    return private_key, public_key

# ==========================================
# Sign
# ==========================================

def sign(message, private_key):
    z = int(sha256_hash(message), 16) % n

    while True:
        k = random.randrange(1, n)
        point = scalar_mult(k, G)
        if point is None:
            continue

        r = point[0] % n
        if r == 0:
            continue

        k_inv = inverse_mod(k, n)
        s = (k_inv * (z + r * private_key)) % n
        if s != 0:
            break

    return (r, s)

# ==========================================
# Verify
# ==========================================

def verify(message, signature, public_key):
    r, s = signature
    if not (1 <= r < n and 1 <= s < n):
        return False

    z = int(sha256_hash(message), 16) % n
    s_inv = inverse_mod(s, n)

    u1 = (z * s_inv) % n
    u2 = (r * s_inv) % n

    P = point_add(
        scalar_mult(u1, G),
        scalar_mult(u2, public_key)
    )

    if P is None:
        return False

    return (P[0] % n) == r

# ==========================================
# Example Usage
# ==========================================

if __name__ == "__main__":
    print("Generating Keys...\n")
    private_key, public_key = generate_keys()
    print("Private Key:", private_key)
    print("Public Key:", public_key)

    message = "Hello ECDSA"
    print("\nSigning Message...")
    signature = sign(message, private_key)
    print("Signature:", signature)

    print("\nVerifying Signature...")
    is_valid = verify(message, signature, public_key)
    print("Valid Signature:", is_valid)
