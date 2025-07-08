from airflow.sdk import dag, task
from datetime import datetime
import time
import base64

@dag(schedule=None, start_date=datetime(2023, 1, 1), catchup=False, tags=['encryption-pipeline'])
def encryption_dag():
    
    @task
    def task1():
        """Generate a very long secret message"""

        secret_message = "The quick brown fox jumps over the lazy dog. " * 3
        print(f"Task 1: Secret message created: '{secret_message}'")
        time.sleep(1)
        return secret_message

    @task
    def task2(secret_message):
        """Split message into chunks for parallel encryption"""
        words = secret_message.split()
        chunks = []
        
        # Split into chunks of 2-3 words each
        chunk_size = 2
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append({
                "chunk_id": i // chunk_size + 1,
                "text": chunk
            })
        
        print(f"Task 2: Split into {len(chunks)} chunks for encryption")
        for chunk in chunks:
            print(f"  Chunk {chunk['chunk_id']}: '{chunk['text']}'")
        
        return chunks
    
    @task
    def encrypt_chunk(chunk_data):
        """Encrypt each chunk (Caesar cipher + Base64)"""
        chunk_id = chunk_data['chunk_id']
        text = chunk_data['text']
        
        print(f"🔒 Encrypting chunk {chunk_id}: '{text}'")
        time.sleep(10)
        
        # Simple Caesar cipher (shift by 3) + Base64
        encrypted_chars = []
        for char in text:
            if char.isalpha():
                shift = 3
                if char.isupper():
                    encrypted_chars.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
                else:
                    encrypted_chars.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
            else:
                encrypted_chars.append(char)
        
        caesar_encrypted = ''.join(encrypted_chars)
        base64_encrypted = base64.b64encode(caesar_encrypted.encode()).decode()
        
        result = {
            "chunk_id": chunk_id,
            "original": text,
            "caesar_cipher": caesar_encrypted,
            "base64_encrypted": base64_encrypted,
            "status": "encrypted"
        }
        
        print(f"✅ Chunk {chunk_id} encrypted!")
        print(f"   Original: '{text}'")
        print(f"   Caesar: '{caesar_encrypted}'")
        print(f"   Base64: '{base64_encrypted}'")
        
        return result
    
    @task
    def task4(all_encrypted_chunks):
        """Decrypt and reassemble the message"""
        print("🔓 Task 4: Decrypting and reassembling message")
        
        chunks_list = list(all_encrypted_chunks)
        decrypted_parts = []
        
        for chunk in sorted(chunks_list, key=lambda x: x['chunk_id']):
            encrypted_text = chunk['base64_encrypted']
            
            # Reverse the encryption: Base64 decode + Caesar decrypt
            caesar_text = base64.b64decode(encrypted_text.encode()).decode()
            
            decrypted_chars = []
            for char in caesar_text:
                if char.isalpha():
                    shift = 3
                    if char.isupper():
                        decrypted_chars.append(chr((ord(char) - ord('A') - shift) % 26 + ord('A')))
                    else:
                        decrypted_chars.append(chr((ord(char) - ord('a') - shift) % 26 + ord('a')))
                else:
                    decrypted_chars.append(char)
            
            decrypted_text = ''.join(decrypted_chars)
            decrypted_parts.append(decrypted_text)
            
            print(f"🔓 Chunk {chunk['chunk_id']}: '{encrypted_text}' → '{decrypted_text}'")
        
        final_message = " ".join(decrypted_parts)
        
        result = {
            "total_chunks": len(chunks_list),
            "decrypted_message": final_message,
            "encryption_method": "Caesar Cipher + Base64",
            "status": "decryption_complete"
        }
        
        print("="*50)
        print("🎉 DECRYPTION COMPLETE!")
        print(f"📝 Final Message: '{final_message}'")
        print(f"🔢 Processed {len(chunks_list)} encrypted chunks")
        print("="*50)
        
        return result
    
    # Workflow
    message = task1()
    chunks = task2(message)
    
    # Parallel encryption
    encrypted_chunks = encrypt_chunk.expand(chunk_data=chunks)
    
    # Final decryption and assembly
    final_result = task4(encrypted_chunks)

encryption_dag()