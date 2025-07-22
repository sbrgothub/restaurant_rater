@echo off
:: This script now only stops the Python applications.
:: The user will close the ngrok window manually.

:: Stop all Python background processes forcefully
taskkill /F /IM python.exe /T > nul

ECHO Python processes stopped.
```**Key Difference:** The `taskkill` command for `ngrok.exe` has been removed.

---

### **The Final PyInstaller Command**

Since your main system no longer launches `ngrok`, you do not need to bundle `ngrok.exe` with your main application anymore. However, you DO need to bundle the new `start_ngrok.bat` that your cashier app will call.

1.  **Create the `start_ngrok.bat` file** that your `cashier_app.py` will launch.
2.  **Clean up:** Delete `dist`, `build`, and `.spec` files.
3.  **Activate venv.**
4.  **Run the new command:**

    ```bash
    pyinstaller --noconsole --name="RestaurantApp" --add-data="feedback.db;." --add-data="start_ngrok.bat;." --add-data="venv;venv" --add-data="start_system.bat;." --add-data="stop_system.bat;." --add-data="web_app;web_app" --add-data="pc_app;pc_app" --add-data="report_generator;report_generator" main_launcher.py
    ```

This setup creates the most logical and user-friendly system. The main launcher starts the Python apps, and the `cashier_app` provides the specific control to launch the internet tunnel when needed.