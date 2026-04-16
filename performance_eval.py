import time
import statistics
from werkzeug.security import generate_password_hash, check_password_hash

def evaluate_hashing_performance(iterations=100):
    """Measures the time taken to hash a password using the framework's scrypt method."""
    print(f"--- Evaluating Password Hashing Performance ({iterations} iterations) ---")
    password = "SecurePassword123!"
    hashing_times = []
    
    for _ in range(iterations):
        start_time = time.perf_counter()
        generate_password_hash(password, method='scrypt')
        end_time = time.perf_counter()
        hashing_times.append(end_time - start_time)
    
    avg_time = statistics.mean(hashing_times) * 1000 # convert to ms
    max_time = max(hashing_times) * 1000
    min_time = min(hashing_times) * 1000
    
    print(f"Average Hashing Time: {avg_time:.2f} ms")
    print(f"Min Time: {min_time:.2f} ms | Max Time: {max_time:.2f} ms")
    print(f"Status: {'Optimal' if avg_time < 300 else 'Suboptimal (Too slow)'}")
    return avg_time

def evaluate_authentication_speed(iterations=100):
    """Measures the time taken to verify a password hash (simulating a login)."""
    print(f"\n--- Evaluating Authentication Speed ({iterations} iterations) ---")
    password = "SecurePassword123!"
    hashed_password = generate_password_hash(password, method='scrypt')
    
    auth_times = []
    for _ in range(iterations):
        start_time = time.perf_counter()
        check_password_hash(hashed_password, password)
        end_time = time.perf_counter()
        auth_times.append(end_time - start_time)
        
    avg_time = statistics.mean(auth_times) * 1000 # convert to ms
    print(f"Average Authentication Time: {avg_time:.2f} ms")
    print(f"Status: {'Secure & Efficient' if 100 < avg_time < 500 else 'Potentially Vulnerable (Too fast) or Inefficient (Too slow)'}")
    return avg_time

if __name__ == "__main__":
    print("FINANCE IDENTITY SECURITY FRAMEWORK - PERFORMANCE EVALUATION\n")
    h_avg = evaluate_hashing_performance(50)
    a_avg = evaluate_authentication_speed(50)
    
    print("\n--- Summary Results ---")
    print(f"Total framework overhead contribution: ~{h_avg + a_avg:.2f} ms per auth cycle.")
    print("Framework utilizes modern Scrypt settings to balance security vs. performance.")
