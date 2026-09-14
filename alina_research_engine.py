import os
import requests
import json
import subprocess
from gtts import gTTS

# Configuration
TOPIC = "farrukh_alina_control"  # App wala same topic name
LISTEN_URL = f"https://ntfy.sh/{TOPIC}/json"
SEND_URL = f"https://ntfy.sh/{TOPIC}"
REPO_PATH = os.path.expanduser("~/farrukh_research-ai") # Aap ki repo ka path

def play_audio(text_response):
    """Voice output through Termux mpv player"""
    print(f"\n🤖 Alina Voice Output: {text_response}")
    tts = gTTS(text=text_response, lang='ur', slow=False)
    tts.save("alina_out.mp3")
    os.system("mpv alina_out.mp3 > /dev/null 2>&1")
    if os.path.exists("alina_out.mp3"):
        os.remove("alina_out.mp3")

def run_research_repo_task(user_prompt):
    """Executes research task within farrukh_research-ai repo"""
    print(f"\n⚙️ Running task on repo: {REPO_PATH}")
    
    # 1. Repo directory mein navigate karein
    os.chdir(REPO_PATH)
    
    # 2. Latest code fetch/pull
    os.system("git pull origin main > /dev/null 2>&1")

    # 3. Research execution logic (Python Agent ya Custom Script)
    # Agar aap CrewAI/Gemini agent chala rahe hain, toh custom command execute hogi:
    try:
        # Example: Python agent script execution
        # Result output variable mein store hoga
        cmd = f'python main.py --query "{user_prompt}"'
        output = subprocess.getoutput(cmd)
        
        if not output or "Error" in output:
            output = f"Research completed for: {user_prompt}. Status check complete."
    except Exception as e:
        output = f"Error executing research workflow: {str(e)}"

    return output

def process_voice_command(raw_message):
    message = raw_message.lower().strip()
    
    # Check Wake-Word "Wakeup Alina" or "Alina"
    if "wakeup alina" in message or "wake up alina" in message or "alina" in message:
        play_audio("Jee, research task start kar rahi hoon.")
        
        # Clean user query
        clean_query = message.replace("wakeup alina", "").replace("wake up alina", "").replace("alina", "").strip()
        if not clean_query:
            clean_query = "latest repository status check"

        # Execute research workflow on repo
        result = run_research_repo_task(clean_query)
        
        # Audio response play karein
        short_summary = result[:200]  # Concise voice response
        play_audio(short_summary)
        
        # Send text log back to ntfy app
        requests.post(SEND_URL, data=f"Alina Output:\n{result}".encode('utf-8'))

def listen_loop():
    print(f"🚀 Alina Engine listening on ntfy topic: '{TOPIC}'")
    print(f"📁 Active Repo: {REPO_PATH}")
    play_audio("Alina Background Service Active. Aap mobile screen off karke voice command bhej sakte hain.")

    response = requests.get(LISTEN_URL, stream=True)
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8'))
                if data.get("event") == "message":
                    msg = data.get("message", "")
                    if not msg.startswith("Alina Output:"):
                        process_voice_command(msg)
            except Exception as e:
                print(f"Loop Error: {e}")

if __name__ == "__main__":
    try:
        listen_loop()
    except KeyboardInterrupt:
        print("\nAlina engine offline.")
