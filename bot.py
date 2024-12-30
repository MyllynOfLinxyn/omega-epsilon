try:
    import tkinter as tk
    from tkinter import messagebox, ttk, filedialog
    import requests
    import os
    import base64
    import sys
    from openai import OpenAI
    import google.generativeai as genai
    from github import Github
    from pathlib import Path
    import json
    import discord
    from PIL import Image, ImageTk
    from io import BytesIO
    import string
    import socket
    import time
    from datetime import datetime
    from zipfile import ZipFile  # Ensure to import ZipFile for handling zip files
    from threading import Thread
except ModuleNotFoundError:
    print("Please install the required modules by running:")
    print("pip install tkinter requests openai google-generativeai PyGithub discord.py pillow") 
    exit(1)

def create_discord_webhook_window():
    # Create main window with modern style
    window = tk.Tk()
    window.title("AI Discord Bot")
    window.geometry("450x600")
    window.configure(bg='#36393F')  # Discord dark theme color
    
    # Set window icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_icon.ico")
    if os.path.isfile(icon_path):
        window.iconbitmap(icon_path)
    else:
        print("Bot icon not found")
    
    style = ttk.Style()
    style.configure('TLabel', background='#36393F', foreground='#DCDDDE')  # Light gray text
    style.configure('TEntry', fieldbackground='#40444B', foreground='#000000')  # Dark text for input fields
    style.configure('TButton', background='#000000', foreground='#000000')  # Discord blurple with black text
    style.configure('TFrame', background='#36393F')
    style.configure('TRadiobutton', foreground='#000000')  # Black text for radiobuttons
    
    main_frame = ttk.Frame(window, padding="25")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Webhook URL section with info button and history
    webhook_frame = ttk.Frame(main_frame)
    webhook_frame.pack(fill=tk.X, pady=(0, 20))

    webhook_label = ttk.Label(webhook_frame, text="WEBHOOK URL", font=('Segoe UI', 9, 'bold'))
    webhook_label.pack(side=tk.LEFT, pady=(0, 5))

    def show_webhook_history():
        history_window = tk.Toplevel(window)
        history_window.title("Webhook History")
        history_window.geometry("400x300")
        history_window.configure(bg='#36393F')

        history_frame = ttk.Frame(history_window, padding="20")
        history_frame.pack(fill=tk.BOTH, expand=True)

        try:
            with open('saved_webhooks.json', 'r') as f:
                webhooks = json.load(f)
        except:
            webhooks = {}

        if not webhooks:
            ttk.Label(history_frame, text="No webhooks saved yet").pack()
            return

        def use_webhook(url):
            webhook_entry.delete(0, tk.END)
            webhook_entry.insert(0, url)
            history_window.destroy()

        ttk.Label(history_frame, text="Previously Used Webhooks:", font=('Segoe UI', 11, 'bold')).pack(pady=(0,10))
        
        for name, url in webhooks.items():
            webhook_item = ttk.Frame(history_frame)
            webhook_item.pack(fill=tk.X, pady=2)
            
            ttk.Label(webhook_item, text=name, wraplength=250).pack(side=tk.LEFT)
            ttk.Button(webhook_item, text="Use", command=lambda u=url: use_webhook(u)).pack(side=tk.RIGHT)

    webhook_history_btn = ttk.Button(webhook_frame, text="📋", width=3, command=show_webhook_history)
    webhook_history_btn.pack(side=tk.RIGHT, padx=(5,0))

    def show_webhook_info():
        webhook_url = webhook_entry.get()
        if not webhook_url:
            messagebox.showerror("Error", "Please enter a webhook URL first")
            return

        try:
            # Get webhook info
            response = requests.get(webhook_url)
            if response.status_code == 200:
                webhook_data = response.json()
                
                # Create info window
                info_window = tk.Toplevel(window)
                info_window.title("Webhook Information")
                info_window.geometry("400x500")
                info_window.configure(bg='#36393F')

                info_frame = ttk.Frame(info_window, padding="20")
                info_frame.pack(fill=tk.BOTH, expand=True)

                # Display webhook info
                ttk.Label(info_frame, text="Webhook Details", font=('Segoe UI', 12, 'bold')).pack(pady=(0,10))
                
                if 'name' in webhook_data:
                    ttk.Label(info_frame, text=f"Name: {webhook_data['name']}").pack(anchor='w')
                
                if 'avatar' in webhook_data:
                    ttk.Label(info_frame, text=f"Avatar URL: {webhook_data['avatar']}").pack(anchor='w')
                
                if 'channel_id' in webhook_data:
                    ttk.Label(info_frame, text=f"Channel ID: {webhook_data['channel_id']}").pack(anchor='w')
                    chat_id_entry.delete(0, tk.END)  # Clear existing entry
                    chat_id_entry.insert(0, webhook_data['channel_id'])  # Set chat ID from webhook data
                
                if 'guild_id' in webhook_data:
                    ttk.Label(info_frame, text=f"Server ID: {webhook_data['guild_id']}").pack(anchor='w')

                # Save webhook option
                def save_webhook():
                    try:
                        with open('saved_webhooks.json', 'r') as f:
                            saved = json.load(f)
                    except:
                        saved = {}
                        
                    saved[webhook_data['name']] = webhook_url
                    
                    with open('saved_webhooks.json', 'w') as f:
                        json.dump(saved, f)
                        
                    messagebox.showinfo("Success", "Webhook saved successfully!")
                    info_window.destroy()

                ttk.Button(info_frame, text="Save Webhook", command=save_webhook).pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get webhook info: {str(e)}")

    webhook_info_btn = ttk.Button(webhook_frame, text="ℹ️", width=3, command=show_webhook_info)
    webhook_info_btn.pack(side=tk.RIGHT, padx=(5,0))
    
    webhook_entry = ttk.Entry(main_frame, width=45)
    webhook_entry.pack(fill=tk.X)
    # Chat ID section  
    chat_id_label = ttk.Label(main_frame, text="CHAT ID", font=('Segoe UI', 9, 'bold'))
    chat_id_label.pack(anchor='w', pady=(0, 5))
    
    chat_id_entry = ttk.Entry(main_frame, width=45)
    chat_id_entry.pack(fill=tk.X, pady=(0, 20))

    # API Keys section
    api_frame = ttk.LabelFrame(main_frame, text="AI API Keys", padding="10")
    api_frame.pack(fill=tk.X, pady=(0, 20))

    # OpenAI section with load button
    openai_frame = ttk.Frame(api_frame)
    openai_frame.pack(fill=tk.X)
    openai_label = ttk.Label(openai_frame, text="OpenAI API Key:")
    openai_label.pack(side=tk.LEFT)
    
    def load_openai_key():
        try:
            with open('saved_settings.json', 'r') as f:
                settings = json.load(f)
                if 'openai_key' in settings:
                    openai_entry.delete(0, tk.END)
                    openai_entry.insert(0, settings['openai_key'])
        except:
            messagebox.showerror("Error", "No saved OpenAI key found")
    
    def save_openai_key():
        api_key = openai_entry.get()
        if not api_key:
            messagebox.showerror("Error", "Please enter an API key first")
            return
        
        try:
            with open('saved_settings.json', 'r') as f:
                settings = json.load(f)
        except:
            settings = {}

        if api_key in settings.values():
            messagebox.showinfo("Info", "This API key is already saved.")
            return
        
        settings['openai_key'] = api_key
        with open('saved_settings.json', 'w') as f:
            json.dump(settings, f)
        
        messagebox.showinfo("Success", "API key saved successfully!")

    ttk.Button(openai_frame, text="📂", width=3, command=load_openai_key).pack(side=tk.RIGHT)
    ttk.Button(openai_frame, text="💾", width=3, command=save_openai_key).pack(side=tk.RIGHT, padx=(5, 0))
    openai_entry = ttk.Entry(api_frame, width=45)
    openai_entry.pack(fill=tk.X, pady=(0, 10))

    # Gemini section with load button
    gemini_frame = ttk.Frame(api_frame)
    gemini_frame.pack(fill=tk.X)
    gemini_label = ttk.Label(gemini_frame, text="Google API Key:")
    gemini_label.pack(side=tk.LEFT)
    
    def load_gemini_key():
        try:
            with open('saved_settings.json', 'r') as f:
                settings = json.load(f)
                if 'gemini_key' in settings:
                    gemini_entry.delete(0, tk.END)
                    gemini_entry.insert(0, settings['gemini_key'])
        except:
            messagebox.showerror("Error", "No saved Gemini key found")
    
    def save_gemini_key():
        api_key = gemini_entry.get()
        if not api_key:
            messagebox.showerror("Error", "Please enter an API key first")
            return
        
        try:
            with open('saved_settings.json', 'r') as f:
                settings = json.load(f)
        except:
            settings = {}

        if api_key in settings.values():
            messagebox.showinfo("Info", "This API key is already saved.")
            return
        
        settings['gemini_key'] = api_key
        with open('saved_settings.json', 'w') as f:
            json.dump(settings, f)
        
        messagebox.showinfo("Success", "API key saved successfully!")

    ttk.Button(gemini_frame, text="📂", width=3, command=load_gemini_key).pack(side=tk.RIGHT)
    ttk.Button(gemini_frame, text="💾", width=3, command=save_gemini_key).pack(side=tk.RIGHT, padx=(5, 0))
    gemini_entry = ttk.Entry(api_frame, width=45)
    gemini_entry.pack(fill=tk.X, pady=(0, 10))

    # GitHub section with load button
    github_frame = ttk.Frame(api_frame)
    github_frame.pack(fill=tk.X)
    github_label = ttk.Label(github_frame, text="GitHub Token:")
    github_label.pack(side=tk.LEFT)
    
    def load_github_key():
        try:
            with open('saved_settings.json', 'r') as f:
                settings = json.load(f)
                if 'github_token' in settings:
                    github_entry.delete(0, tk.END)
                    github_entry.insert(0, settings['github_token'])
        except:
            messagebox.showerror("Error", "No saved GitHub token found")
    
    def save_github_key():
        token = github_entry.get()
        if not token:
            messagebox.showerror("Error", "Please enter a token first")
            return
        
        try:
            with open('saved_settings.json', 'r') as f:
                settings = json.load(f)
        except:
            settings = {}

        if token in settings.values():
            messagebox.showinfo("Info", "This token is already saved.")
            return
        
        settings['github_token'] = token
        with open('saved_settings.json', 'w') as f:
            json.dump(settings, f)
        
        messagebox.showinfo("Success", "Token saved successfully!")

    ttk.Button(github_frame, text="📂", width=3, command=load_github_key).pack(side=tk.RIGHT)
    ttk.Button(github_frame, text="💾", width=3, command=save_github_key).pack(side=tk.RIGHT, padx=(5, 0))
    github_entry = ttk.Entry(api_frame, width=45)
    github_entry.pack(fill=tk.X)

    def validate_openai_key():
        api_key = openai_entry.get()
        if not api_key:
            return False
        try:
            client = OpenAI(api_key=api_key)
            client.models.list()  # Test API call
            return True
        except Exception:
            return False

    def validate_gemini_key():
        api_key = gemini_entry.get()
        if not api_key:
            return False
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            model.generate_content("test")  # Test API call
            return True
        except Exception:
            return False

    def validate_github_token():
        token = github_entry.get()
        if not token:
            return False
        try:
            g = Github(token)
            g.get_user().login  # Test API call
            return True
        except Exception:
            return False

    # Message section
    message_label = ttk.Label(main_frame, text="MESSAGE", font=('Segoe UI', 9, 'bold'))
    message_label.pack(anchor='w', pady=(0, 5))
    
    message_text = tk.Text(main_frame, width=40, height=8, bg='#40444B', fg='#000000', 
                          font=('Segoe UI', 10), relief='flat', padx=8, pady=8)
    message_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

    # File Upload section
    file_frame = ttk.Frame(main_frame)
    file_frame.pack(fill=tk.X, pady=(0, 10))
    
    file_path = tk.StringVar()
    
    def select_file():
        file_path_selected = filedialog.askopenfilename(
            filetypes=[
                ("All Files", "*.*"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Videos", "*.mp4 *.avi *.mov *.mkv"),
                ("Audio", "*.mp3 *.wav *.ogg"),
                ("Documents", "*.txt *.pdf *.doc *.docx")
            ]
        )
        if file_path_selected:
            file_path.set(file_path_selected)
            file_label.config(text=f"Selected: {Path(file_path_selected).name}")
    
    def send_file():
        if not file_path.get():
            messagebox.showerror("Error", "Please select a file first")
            return
            
        webhook_url = webhook_entry.get()
        chat_id = chat_id_entry.get()
        
        if not webhook_url or not chat_id:
            messagebox.showerror("Error", "Please fill in webhook URL and chat ID")
            return
            
        try:
            with open(file_path.get(), 'rb') as file:
                files = {'file': file}
                response = requests.post(webhook_url, files=files)
                
            if response.status_code == 204:
                # Verify if image was sent by checking Discord channel
                verify_response = requests.get(f"{webhook_url}/messages")
                if verify_response.status_code == 200:
                    messages = verify_response.json()
                    latest_message = messages[0] if messages else None
                    
                    if latest_message and latest_message.get('attachments'):
                        message_logs.append(f"File sent and verified successfully")
                        messagebox.showinfo("Success", "File sent and verified successfully!")
                    else:
                        message_logs.append("File sent but not verified in channel")
                        messagebox.showwarning("Warning", "File sent but could not verify in channel")
                else:
                    message_logs.append("File sent but verification failed")
                    messagebox.showwarning("Warning", "File sent but verification failed")
                    
                file_path.set("")
                file_label.config(text="No file selected")
            else:
                message_logs.append("Failed to send file")
                messagebox.showerror("Error", "Failed to send file")
                
        except Exception as e:
            message_logs.append(f"Error sending file: {str(e)}")
            messagebox.showerror("Error", f"Error sending file: {str(e)}")
    
    select_file_button = ttk.Button(file_frame, text="Select File", command=select_file)
    select_file_button.pack(side=tk.LEFT)
    
    send_file_button = ttk.Button(file_frame, text="Send File", command=send_file)
    send_file_button.pack(side=tk.LEFT, padx=5)
    
    file_label = ttk.Label(file_frame, text="No file selected")
    file_label.pack(side=tk.LEFT, padx=(10, 0))

    # List to store message logs
    message_logs = []

    selected_ai = tk.StringVar()
    
    def select_ai():
        ai_window = tk.Toplevel(window)
        ai_window.title("Select AI Model")
        ai_window.geometry("300x200")
        ai_window.configure(bg='#36393F')
        
        ai_frame = ttk.Frame(ai_window, padding="20")
        ai_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Radiobutton(ai_frame, text="ChatGPT", value="gpt", variable=selected_ai).pack(pady=5)
        ttk.Radiobutton(ai_frame, text="Gemini", value="gemini", variable=selected_ai).pack(pady=5)
        ttk.Radiobutton(ai_frame, text="GitHub Copilot", value="copilot", variable=selected_ai).pack(pady=5)
        
        def confirm():
            if selected_ai.get():
                # Validate API key based on selected AI
                is_valid = False
                if selected_ai.get() == "gpt":
                    is_valid = validate_openai_key()
                elif selected_ai.get() == "gemini":
                    is_valid = validate_gemini_key()
                elif selected_ai.get() == "copilot":
                    is_valid = validate_github_token()
                
                if is_valid:
                    messagebox.showinfo("Success", f"Selected {selected_ai.get().upper()} - API key validated successfully!")
                    ai_window.destroy()
                else:
                    messagebox.showerror("Error", "Invalid API key for selected AI model")
        
        ttk.Button(ai_frame, text="Confirm", command=confirm).pack(pady=20)

    def send_ai_message():
        webhook_url = webhook_entry.get()
        chat_id = chat_id_entry.get()
        message = message_text.get("1.0", tk.END).strip()
        
        if not webhook_url or not chat_id or not message or not selected_ai.get():
            messagebox.showerror("Error", "Please fill in all fields and select an AI model")
            return
            
        try:
            ai_response = ""
            query = message
            
            if selected_ai.get() == "gpt":
                if not validate_openai_key():
                    messagebox.showerror("Error", "Invalid OpenAI API key")
                    return
                client = OpenAI(api_key=openai_entry.get())
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": query}],
                    model="gpt-4"
                )
                ai_response = response.choices[0].message.content
                
            elif selected_ai.get() == "gemini":
                if not validate_gemini_key():
                    messagebox.showerror("Error", "Invalid Google API key")
                    return
                genai.configure(api_key=gemini_entry.get())
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(query)
                ai_response = response.text
                
            elif selected_ai.get() == "copilot":
                if not validate_github_token():
                    messagebox.showerror("Error", "Invalid GitHub token")
                    return
                g = Github(github_entry.get())
                ai_response = "GitHub Copilot response would go here"
            
            if ai_response:
                payload = {"content": f"Response to '{query}':\n{ai_response}"}
                response = requests.post(webhook_url, json=payload)
                
                if response.status_code == 204:
                    message_logs.append(f"AI response sent successfully")
                    messagebox.showinfo("Success", "AI response sent successfully!")
                    message_text.delete("1.0", tk.END)
                else:
                    message_logs.append(f"Failed to send AI response")
                    messagebox.showerror("Error", "Failed to send AI response")
                    
        except Exception as e:
            message_logs.append(f"Error sending AI message: {str(e)}")
            messagebox.showerror("Error", f"Error sending AI message: {str(e)}")
    
    def test_webhook():
        webhook_url = webhook_entry.get()
        chat_id = chat_id_entry.get()
        
        if not webhook_url or not chat_id:
            messagebox.showerror("Error", "Please fill in webhook URL and chat ID")
            return
            
        try:
            # Test webhook connection
            test_message = "🔄 Testing connections...\n\n"
            
            # Test OpenAI API
            if validate_openai_key():
                test_message += "✅ OpenAI API: Connected successfully\n"
            else:
                test_message += "❌ OpenAI API: Connection failed\n"
                
            # Test Gemini API
            if validate_gemini_key():
                test_message += "✅ Gemini API: Connected successfully\n"
            else:
                test_message += "❌ Gemini API: Connection failed\n"
                
            # Test GitHub API
            if validate_github_token():
                test_message += "✅ GitHub API: Connected successfully\n"
            else:
                test_message += "❌ GitHub API: Connection failed\n"
            
            # Send test results to Discord
            payload = {"content": test_message}
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code == 204:
                message_logs.append("Connection test results sent to Discord")
                messagebox.showinfo("Success", "Connection test results sent to Discord!")
            else:
                message_logs.append("Failed to send test results")
                messagebox.showerror("Error", "Failed to send test results to Discord")
                
        except Exception as e:
            message_logs.append(f"Connection test error: {str(e)}")
            messagebox.showerror("Error", f"Error during connection test: {str(e)}")


    def show_logs():
        logs_window = tk.Toplevel(window)
        logs_window.title("Message Logs")
        logs_window.geometry("400x300")
        logs_window.configure(bg='#36393F')
        
        logs_frame = ttk.Frame(logs_window, padding="20")
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        logs_text = tk.Text(logs_frame, width=40, height=12, bg='#40444B', fg='#000000',
                           font=('Segoe UI', 10), relief='flat', padx=8, pady=8)
        logs_text.pack(fill=tk.BOTH, expand=True)
        
        for log in message_logs:
            logs_text.insert(tk.END, log + "\n")
        
        logs_text.config(state=tk.DISABLED)

    def show_bot_info():
        webhook_url = webhook_entry.get()
        chat_id = chat_id_entry.get()

        if not webhook_url or not chat_id:
            messagebox.showerror("Error", "Please fill in webhook URL and chat ID")
            return

        try:
            # Get webhook info
            response = requests.get(webhook_url)
            if response.status_code == 200:
                webhook_data = response.json()

                # Create info window
                info_window = tk.Toplevel(window)
                info_window.title("Bot Information")
                info_window.geometry("500x600")
                info_window.configure(bg='#36393F')

                info_frame = ttk.Frame(info_window, padding="20")
                info_frame.pack(fill=tk.BOTH, expand=True)

                # Display webhook avatar
                if webhook_data.get('avatar'):
                    avatar_url = f"https://cdn.discordapp.com/avatars/{webhook_data['id']}/{webhook_data['avatar']}.png"
                    response = requests.get(avatar_url)
                    if response.status_code == 200:
                        avatar_image = Image.open(BytesIO(response.content))
                        avatar_image = avatar_image.resize((100, 100))
                        avatar_photo = ImageTk.PhotoImage(avatar_image)
                        avatar_label = ttk.Label(info_frame, image=avatar_photo)
                        avatar_label.image = avatar_photo
                        avatar_label.pack(pady=(0, 20))

                # Display webhook info
                ttk.Label(info_frame, text=f"Webhook ID: {webhook_data.get('id', 'N/A')}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
                ttk.Label(info_frame, text=f"Current Webhook URL: {webhook_url}", font=('Segoe UI', 10), wraplength=400).pack(anchor='w', pady=2)
                ttk.Label(info_frame, text=f"Channel ID: {webhook_data.get('channel_id', 'N/A')}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
                ttk.Label(info_frame, text=f"Server ID: {webhook_data.get('guild_id', 'N/A')}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
                
                # Check if webhook is online
                online_status = "✅ Online" if response.status_code == 200 else "❌ Offline"
                ttk.Label(info_frame, text=f"Status: {online_status}", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=2)

                # API Status
                ttk.Label(info_frame, text="\nAPI Status:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(20,5))
                openai_status = "✅ Connected" if validate_openai_key() else "❌ Disconnected"
                gemini_status = "✅ Connected" if validate_gemini_key() else "❌ Disconnected"
                github_status = "✅ Connected" if validate_github_token() else "❌ Disconnected"

                ttk.Label(info_frame, text=f"OpenAI API: {openai_status}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
                ttk.Label(info_frame, text=f"Gemini API: {gemini_status}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
                ttk.Label(info_frame, text=f"GitHub API: {github_status}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get bot info: {str(e)}")

    def show_queries():
        queries_window = tk.Toplevel(window)
        queries_window.title("Consultas")
        queries_window.geometry("300x200")
        queries_window.configure(bg='#36393F')

        queries_frame = ttk.Frame(queries_window, padding="20")
        queries_frame.pack(fill=tk.BOTH, expand=True)




        def show_number_window():
            number_window = tk.Toplevel(queries_window)
            number_window.title("Consulta Número")
            number_window.geometry("400x300")
            number_window.configure(bg='#36393F')

            number_frame = ttk.Frame(number_window, padding="20")
            number_frame.pack(fill=tk.BOTH, expand=True)

            number_frame_input = ttk.Frame(number_frame)
            number_frame_input.pack(fill=tk.X)

            number_entry = ttk.Entry(number_frame_input, width=30)
            number_entry.pack(side=tk.LEFT, padx=(0, 5))

            format_label = ttk.Label(number_frame, text="")
            format_label.pack(pady=10)

            output_text = tk.Text(number_frame, height=10, width=50, wrap=tk.WORD)
            output_text.pack(pady=(10, 0))
            output_text.config(state=tk.DISABLED)  # Make it read-only

            # Dictionary of country codes, flags and number formats
            country_info = {
                '1': {'flag': '🇺🇸', 'name': 'Estados Unidos', 'format': '+1 (XXX) XXX-XXXX'},  # USA
                '55': {'flag': '🇧🇷', 'name': 'Brasil', 'format': '+55 (XX) XXXXX-XXXX'},  # Brazil
                '44': {'flag': '🇬🇧', 'name': 'Reino Unido', 'format': '+44 XXXX XXXXXX'},  # UK
                '351': {'flag': '🇵🇹', 'name': 'Portugal', 'format': '+351 XXX XXX XXX'},  # Portugal
                '34': {'flag': '🇪🇸', 'name': 'Espanha', 'format': '+34 XXX XX XX XX'},  # Spain
                '33': {'flag': '🇫🇷', 'name': 'França', 'format': '+33 X XX XX XX XX'},  # France
                '49': {'flag': '🇩🇪', 'name': 'Alemanha', 'format': '+49 XXX XXXXXXXX'},  # Germany
                '39': {'flag': '🇮🇹', 'name': 'Itália', 'format': '+39 XXX XXX XXXX'},  # Italy
                '81': {'flag': '🇯🇵', 'name': 'Japão', 'format': '+81 XX XXXX XXXX'},  # Japan
                '86': {'flag': '🇨🇳', 'name': 'China', 'format': '+86 XXX XXXX XXXX'},  # China
                '7': {'flag': '🇷🇺', 'name': 'Rússia', 'format': '+7 XXX XXX-XX-XX'},  # Russia
                '52': {'flag': '🇲🇽', 'name': 'México', 'format': '+52 XX XXXX XXXX'},  # Mexico
                '54': {'flag': '🇦🇷', 'name': 'Argentina', 'format': '+54 XX XXXX-XXXX'},  # Argentina
                '56': {'flag': '🇨🇱', 'name': 'Chile', 'format': '+56 X XXXX XXXX'},  # Chile
                '57': {'flag': '🇨🇴', 'name': 'Colômbia', 'format': '+57 XXX XXX XXXX'},  # Colombia
                '51': {'flag': '🇵🇪', 'name': 'Peru', 'format': '+51 XXX XXX XXX'},  # Peru
                '61': {'flag': '🇦🇺', 'name': 'Austrália', 'format': '+61 XXX XXX XXX'},  # Australia
                '64': {'flag': '🇳🇿', 'name': 'Nova Zelândia', 'format': '+64 X XXX XXXX'},  # New Zealand
                '82': {'flag': '🇰🇷', 'name': 'Coreia do Sul', 'format': '+82 XX XXXX XXXX'},  # South Korea
                '91': {'flag': '🇮🇳', 'name': 'Índia', 'format': '+91 XXXXX XXXXX'},  # India
                '380': {'flag': '🇺🇦', 'name': 'Ucrânia', 'format': '+380 XX XXX XXXX'},  # Ukraine
                '48': {'flag': '🇵🇱', 'name': 'Polônia', 'format': '+48 XXX XXX XXX'},  # Poland
                '46': {'flag': '🇸🇪', 'name': 'Suécia', 'format': '+46 XX XXX XXXX'},  # Sweden
                '47': {'flag': '🇳🇴', 'name': 'Noruega', 'format': '+47 XXX XX XXX'},  # Norway
                '45': {'flag': '🇩🇰', 'name': 'Dinamarca', 'format': '+45 XXXX XXXX'},  # Denmark
                '358': {'flag': '🇫🇮', 'name': 'Finlândia', 'format': '+358 XX XXX XXXX'},  # Finland
                '31': {'flag': '🇳🇱', 'name': 'Holanda', 'format': '+31 X XXXX XXXX'},  # Netherlands
                '32': {'flag': '🇧🇪', 'name': 'Bélgica', 'format': '+32 XXX XX XX XX'},  # Belgium
                '41': {'flag': '🇨🇭', 'name': 'Suíça', 'format': '+41 XX XXX XXXX'},  # Switzerland
            }

            def on_number_change(*args):
                number = number_entry.get().strip()
                if not number:
                    format_label.config(text="")
                    return

                clean_number = ''.join(filter(str.isdigit, number))
                country_code = None
                
                for code in sorted(country_info.keys(), key=len, reverse=True):
                    if clean_number.startswith(code):
                        country_code = code
                        country_data = country_info[code]
                        format_label.config(text=f"{country_data['flag']} Formato: {country_data['format']}")
                        break
                
                if not country_code:
                    format_label.config(text="País não identificado")

            number_entry.bind('<KeyRelease>', on_number_change)

            def check_number():
                number = number_entry.get().strip()
                if not number:
                    messagebox.showerror("Error", "Por favor, insira um número")
                    return

                # Clean the number and extract country code
                clean_number = ''.join(filter(str.isdigit, number))
                country_code = None
                
                # Try to match the longest country code first
                for code in sorted(country_info.keys(), key=len, reverse=True):
                    if clean_number.startswith(code):
                        country_code = code
                        break

                if country_code:
                    country_data = country_info[country_code]
                    
                    # Get location data from API for Brazilian numbers
                    location_data = {'cidade': 'N/A', 'estado': 'N/A'}
                    if country_code == '55':
                        try:
                            # Using Brasil API to get location data
                            ddd = clean_number[2:4]  # Get DDD (area code)
                            api_url = f'https://brasilapi.com.br/api/ddd/v1/{ddd}'
                            response = requests.get(api_url)
                            
                            if response.status_code == 200:
                                api_data = response.json()
                                # Get first city from the list as example
                                location_data['cidade'] = api_data['cities'][0] if api_data['cities'] else 'N/A'
                                location_data['estado'] = api_data['state']
                        except Exception as e:
                            print(f"Error getting location data: {str(e)}")
                    
                    # Additional data with real location info when available
                    additional_data = {
                        'cidade': location_data['cidade'],
                        'estado': location_data['estado'],
                        'cep': 'N/A',
                        'operadora': 'N/A',
                        'tipo': 'Celular' if len(clean_number) > 10 else 'Fixo',
                        'portabilidade': 'N/A',
                        'status': 'Ativo',
                        'categoria': 'Pessoa Física',
                        'data_ativacao': 'N/A',
                        'plano': 'N/A'
                    }
                    
                    result_text = f"""
Número: {number}
Código do País (DDI): +{country_code}
País: {country_data['flag']} {country_data['name']}
Formato: {country_data['format']}

Informações Adicionais:
Cidade: {additional_data['cidade']}
Estado: {additional_data['estado']}
CEP: {additional_data['cep']}
Operadora: {additional_data['operadora']}
Tipo: {additional_data['tipo']}
Portabilidade: {additional_data['portabilidade']}
Status: {additional_data['status']}
Categoria: {additional_data['categoria']}
Data de Ativação: {additional_data['data_ativacao']}
Plano: {additional_data['plano']}
"""
                    output_text.config(state=tk.NORMAL)
                    output_text.delete(1.0, tk.END)  # Clear previous output
                    output_text.insert(tk.END, result_text)  # Insert new output
                    output_text.config(state=tk.DISABLED)  # Make it read-only
                else:
                    messagebox.showwarning("Aviso", "País não identificado para este número")

            ttk.Button(number_frame_input, text="Consultar", command=check_number).pack(side=tk.LEFT)

        ttk.Button(queries_frame, text="Number", command=show_number_window).pack(pady=10)

        def show_email_window():
            email_window = tk.Toplevel(queries_window)
            email_window.title("Consulta Email")
            email_window.geometry("400x300")
            email_window.configure(bg='#36393F')

            email_frame = ttk.Frame(email_window, padding="20")
            email_frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(email_frame, text="Digite o email:").pack(pady=(0,5))
            email_entry = ttk.Entry(email_frame, width=40)
            email_entry.pack(pady=(0,10))

            output_text = tk.Text(email_frame, height=10, width=50, wrap=tk.WORD)
            output_text.pack(pady=(10, 0))
            output_text.config(state=tk.DISABLED)  # Make it read-only

            def check_email():
                email = email_entry.get().strip()
                if not email or '@' not in email:
                    messagebox.showerror("Erro", "Por favor, insira um email válido")
                    return

                # Parse email parts
                username, domain = email.split('@')
                domain_parts = domain.split('.')
                
                # Detect email provider
                provider = "Desconhecido"
                if "gmail" in domain:
                    provider = "Gmail (Google)"
                elif "hotmail" in domain or "outlook" in domain or "live" in domain:
                    provider = "Microsoft (Hotmail/Outlook)"
                elif "yahoo" in domain:
                    provider = "Yahoo Mail"
                elif "protonmail" in domain:
                    provider = "ProtonMail"
                elif "icloud" in domain:
                    provider = "iCloud (Apple)"

                # Detect country from TLD
                country = "Internacional (.com)"
                if domain.endswith('.br'):
                    country = "Brasil (.com.br)"
                elif domain.endswith('.uk'):
                    country = "Reino Unido (.co.uk)"
                elif domain.endswith('.pt'):
                    country = "Portugal (.pt)"
                elif domain.endswith('.es'):
                    country = "Espanha (.es)"
                elif domain.endswith('.fr'):
                    country = "França (.fr)"
                elif domain.endswith('.de'):
                    country = "Alemanha (.de)"
                
                # Initialize variables with N/A
                is_valid = "N/A"
                is_disposable = "N/A"
                score = "N/A"
                city = "N/A"
                region = "N/A"
                phone_number = "N/A"
                connected_emails = "N/A"
                logged_in_sites = "N/A"
                social_media_accounts = "N/A"
                
                # Try to get additional info from email verification API
                try:
                    api_url = f"https://emailvalidation.abstractapi.com/v1/?api_key=YOUR_API_KEY&email={email}"
                    response = requests.get(api_url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        is_valid = data.get('is_valid', "N/A")
                        is_disposable = data.get('is_disposable_email', "N/A")
                        score = data.get('quality_score', "N/A")
                        city = data.get('city', "N/A")
                        region = data.get('region', "N/A")
                        phone_number = data.get('phone_number', "N/A")
                        connected_emails = data.get('connected_emails', "N/A")
                        logged_in_sites = data.get('logged_in_sites', "N/A")
                        social_media_accounts = data.get('social_media_accounts', "N/A")
                except:
                    pass

                result = f"""
Email: {email}
Provedor: {provider}
País: {country}
Usuário: {username}
Domínio: {domain}

Informações Adicionais:
Email Válido: {is_valid}
Email Descartável: {is_disposable}
Score de Qualidade: {score}

Localização:
Cidade: {city}
Estado: {region}

Informações de Contato:
Telefone: {phone_number}

Contas Vinculadas:
Gmail Conectados: {connected_emails}

Sites Logados:
{logged_in_sites}

Redes Sociais:
{social_media_accounts}
"""

                output_text.config(state=tk.NORMAL)
                output_text.delete(1.0, tk.END)  # Clear previous output
                output_text.insert(tk.END, result)  # Insert new output
                output_text.config(state=tk.DISABLED)  # Make it read-only

            ttk.Button(email_frame, text="Consultar", command=check_email).pack(pady=10)
        ttk.Button(queries_frame, text="Email", command=show_email_window).pack(pady=10)

        def show_snipper_window():
            snipper_window = tk.Toplevel(queries_window)
            snipper_window.title("Consulta de Geolocalização de IP")
            snipper_window.geometry("400x300")
            snipper_window.configure(bg='#36393F')

            snipper_frame = ttk.Frame(snipper_window, padding="20")
            snipper_frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(snipper_frame, text="Digite o IP para consulta:").pack(pady=(0,5))
            ip_entry = ttk.Entry(snipper_frame, width=40)
            ip_entry.pack(pady=(0,10))

            output_text = tk.Text(snipper_frame, height=10, width=50, wrap=tk.WORD)
            output_text.pack(pady=(10, 0))
            output_text.config(state=tk.DISABLED)  # Make it read-only

            def check_ip_geolocation():
                ip_input = ip_entry.get().strip()
                if not ip_input:
                    messagebox.showerror("Erro", "Por favor, insira um IP válido")
                    return
                try:
                    response = requests.get(f"http://ip-api.com/json/{ip_input}")
                    if response.status_code == 200:
                        data = response.json()
                        result = f"""
IP: {data.get('query', 'N/A')}
Status: {data.get('status', 'N/A')}
País: {data.get('country', 'N/A')}
Código do País: {data.get('countryCode', 'N/A')}
Região: {data.get('region', 'N/A')}
Nome da Região: {data.get('regionName', 'N/A')}
Cidade: {data.get('city', 'N/A')}
Código Postal: {data.get('zip', 'N/A')}
Latitude: {data.get('lat', 'N/A')}
Longitude: {data.get('lon', 'N/A')}
Timezone: {data.get('timezone', 'N/A')}
ISP: {data.get('isp', 'N/A')}
Organização: {data.get('org', 'N/A')}
Tipo: {data.get('as', 'N/A')}
"""
                    else:
                        result = "Erro ao consultar a geolocalização do IP."

                    output_text.config(state=tk.NORMAL)
                    output_text.delete(1.0, tk.END)  # Clear previous output
                    output_text.insert(tk.END, result)  # Insert new output
                    output_text.config(state=tk.DISABLED)  # Make it read-only

                except Exception as e:
                    messagebox.showerror("Erro", f"Falha ao consultar geolocalização: {str(e)}")

            ttk.Button(snipper_frame, text="Consultar Geolocalização", command=check_ip_geolocation).pack(pady=10)

        ttk.Button(queries_frame, text="Snipper", command=show_snipper_window).pack(pady=10)








        def show_roblox_window():
            roblox_window = tk.Toplevel(queries_window)
            roblox_window.title("Consulta Roblox")
            roblox_window.geometry("400x300")
            roblox_window.configure(bg='#36393F')

            roblox_frame = ttk.Frame(roblox_window, padding="20")
            roblox_frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(roblox_frame, text="Digite o nome de usuário do Roblox:").pack(pady=(0,5))
            roblox_entry = ttk.Entry(roblox_frame, width=40)
            roblox_entry.pack(pady=(0,10))

            output_text = tk.Text(roblox_frame, height=10, width=50, wrap=tk.WORD)
            output_text.pack(pady=(10, 0))
            output_text.config(state=tk.DISABLED)  # Make it read-only

            def check_roblox():
                username_input = roblox_entry.get().strip()
                if not username_input:
                    messagebox.showerror("Erro", "Por favor, insira um nome de usuário válido")
                    return

                try:
                    response = requests.post("https://users.roblox.com/v1/usernames/users", json={
                        "usernames": [username_input],
                        "excludeBannedUsers": "true"
                    })

                    data = response.json()
                    user_id = data['data'][0]['id']

                    response = requests.get(f"https://users.roblox.com/v1/users/{user_id}")
                    api = response.json()

                    userid = api.get('id', "None")
                    display_name = api.get('displayName', "None")
                    username = api.get('name', "None")
                    description = api.get('description', "None")
                    created_at = api.get('created', "None")
                    is_banned = api.get('isBanned', "None")
                    external_app_display_name = api.get('externalAppDisplayName', "None")
                    has_verified_badge = api.get('hasVerifiedBadge', "None")

                    result = f"""
Username       : {username}
Id             : {userid}
Display Name   : {display_name}
Description    : {description}
Created        : {created_at}
Banned         : {is_banned}
External Name  : {external_app_display_name}
Verified Badge : {has_verified_badge}
"""
                    output_text.config(state=tk.NORMAL)
                    output_text.delete(1.0, tk.END)  # Clear previous output
                    output_text.insert(tk.END, result)  # Insert new output
                    output_text.config(state=tk.DISABLED)  # Make it read-only
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao obter informações do usuário: {str(e)}")

            ttk.Button(roblox_frame, text="Consultar", command=check_roblox).pack(pady=10)
        ttk.Button(queries_frame, text="Roblox", command=show_roblox_window).pack(pady=10)



    # Button section with modern styling
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(0, 0))
    
    # Custom button style
    style.configure('Custom.TButton', padding=10, foreground='#000000')  # Black text for buttons
    
    select_ai_button = ttk.Button(button_frame, text="Select AI", command=select_ai, style='Custom.TButton')
    select_ai_button.pack(side=tk.LEFT, padx=(0, 5), expand=True)
    
    test_button = ttk.Button(button_frame, text="Test Connection", command=test_webhook, style='Custom.TButton')
    test_button.pack(side=tk.LEFT, padx=(0, 5), expand=True)
    
    ai_message_button = ttk.Button(button_frame, text="AI Message", command=send_ai_message, style='Custom.TButton')
    ai_message_button.pack(side=tk.LEFT, padx=5, expand=True)
    
    info_bot_button = ttk.Button(button_frame, text="Info Bot", command=show_bot_info, style='Custom.TButton')
    info_bot_button.pack(side=tk.LEFT, padx=5, expand=True)
    
    logs_button = ttk.Button(button_frame, text="Show Logs", command=show_logs, style='Custom.TButton')
    logs_button.pack(side=tk.LEFT, padx=(5, 0), expand=True)

    queries_button = ttk.Button(button_frame, text="Consultas", command=show_queries, style='Custom.TButton')
    queries_button.pack(side=tk.LEFT, padx=(5, 0), expand=True)

    try:
        window.mainloop()
    except ImportError:
        print("Required modules not found. Please install them by running:")
        print("pip install tkinter requests openai google-generativeai PyGithub discord.py pillow")
        sys.exit(1)

if __name__ == "__main__":
    create_discord_webhook_window()
