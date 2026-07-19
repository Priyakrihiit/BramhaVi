#!/usr/bin/env python3

# Cryptographic Certificate Generator - BrahmaVidya Galaxy
# Purpose: Generates digital signature hashes for verifiable learner completions.

import hashlib
import json
import time

def generate_certificate_hash(recipient_id, course_id, secret_salt):
    timestamp = str(int(time.time()))
    seed = f"{recipient_id}:{course_id}:{timestamp}:{secret_salt}".encode('utf-8')
    signature = hashlib.sha256(seed).hexdigest()
    
    return {
        "hash": signature,
        "issued_at": timestamp,
        "recipient": recipient_id,
        "course": course_id
    }

if __name__ == "__main__":
    # Standard testing generation
    print(json.dumps(generate_certificate_hash("usr_123", "crs_abc", "super_secret_salt")))
