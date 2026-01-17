import subprocess
import time
import requests
import sys
import os

def test_server():
    print("Starting server for testing...")
    # Start server as a subprocess
    process = subprocess.Popen(
        [sys.executable, "pocket_tts_openai_server.py", "--port", "5001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait for valid startup
        print("Waiting for server to start...")
        time.sleep(15) # Give it time to load model
        
        base_url = "http://localhost:5001"
        
        # 1. Test Home
        try:
            r = requests.get(base_url + "/")
            print(f"GET /: {r.status_code}")
            if r.status_code == 200 and "Pocket TTS" in r.text:
                print("SUCCESS: Home page loaded.")
            else:
                print("FAILURE: Home page check failed.")
        except Exception as e:
            print(f"FAILURE: Could not connect to home page: {e}")

        # 2. Test Voices List
        try:
            r = requests.get(base_url + "/v1/voices")
            print(f"GET /v1/voices: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                if data.get("object") == "list" and len(data.get("data", [])) > 0:
                    print(f"SUCCESS: Voices list returned {len(data['data'])} voices.")
                else:
                    print("FAILURE: Voices list format incorrect.")
            else:
                print("FAILURE: Voices endpoint returned error.")
        except Exception as e:
            print(f"FAILURE: Voices test failed: {e}")

        # 3. Test Generation (Mock or Real)
        payload = {
            "model": "pocket-tts",
            "input": "Hi",
            "voice": "hf://kyutai/tts-voices/alba-mackenna/casual.wav", 
            "response_format": "wav"
        }
        try:
            t0 = time.time()
            r = requests.post(base_url + "/v1/audio/speech", json=payload, timeout=60)
            print(f"POST /v1/audio/speech: {r.status_code} (took {time.time()-t0:.2f}s)")
            if r.status_code == 200:
                print(f"SUCCESS: Audio generated ({len(r.content)} bytes).")
            else:
                print(f"FAILURE: Generation failed: {r.text}")
        except Exception as e:
            print(f"FAILURE: Generation test failed: {e}")

    finally:
        print("Terminating server...")
        process.terminate()
        try:
            outs, errs = process.communicate(timeout=5)
            # print("Server Output:", outs)
            # print("Server Errors:", errs)
        except:
            process.kill()

if __name__ == "__main__":
    test_server()
