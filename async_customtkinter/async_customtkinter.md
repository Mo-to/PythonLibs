# AsyncCTK - Asynchronous CustomTkinter GUI

## General
`AsyncCTK` is an enhanced version of `CustomTkinter` that allows the seamless integration of asynchronous programming with a Tkinter-based GUI. It overcomes the limitation of traditional `Tkinter` and its `root.after()` management by enabling the use of `asyncio` coroutines for background tasks, periodic updates, and async button commands, all while maintaining a responsive user interface.

The purpose of this library is to allow developers to:
- Use async background tasks (e.g., periodic updates, network calls) alongside a CustomTkinter GUI
- Execute async functions via GUI commands, like button clicks.
- Avoid GUI freezing and blocking operations common with synchronous tasks.

## Disclaimer
The implementation is heavily inspired by [insolor's async-tkinter-loop](https://github.com/insolor/async-tkinter-loop/tree/main).  
**I do not claim to came up with this on my own!**  
I just added additional features with a better interface for my use case and i came to a point where adjusting the async-tkinter-loop codebase was not enough anymore.

## Usage

The following example explains the main features of `AsyncCTK` and how to use them in your projects:

### Example Code

```python
import asyncio
import time
import customtkinter as ctk
from async_customtkinter import AsyncCTK


class ExampleGUI(AsyncCTK):
    def __init__(self, update_interval: int = 1000):
        super().__init__(update_interval)

        # Create a label that updates the time using an async background task
        time_label = ctk.CTkLabel(self, text="", font=("Arial", 16))
        time_label.pack(pady=20)

        # Background task to update the time
        async def update_time():
            time_label.configure(text=time.strftime("%H:%M:%S"))
            await asyncio.sleep(1.1)  # will lead to a warning, because update takes longer than update_interval

        self.add_update_func(update_time)

        # Create a button with an async command function
        button = ctk.CTkButton(self, text="Click me", command=self.execute_async_command(self.async_show_popup))
        button.pack(padx=20, pady=20)

    async def async_show_popup(self):
        # Wait 2 seconds to demonstrate async
        await asyncio.sleep(2)
        popup = ctk.CTkToplevel(self)
        popup.geometry("300x150")
        popup.grab_set()
        ctk.CTkLabel(popup, text="This was an async alert!", font=("Arial", 16)).pack(pady=20)
        ctk.CTkButton(popup, text="Its working", command=popup.destroy).pack(pady=10)


if __name__ == "__main__":
    my_example = ExampleGUI()
    asyncio.run(my_example.mainloop())
```

### Explanation
1. **Async Background Tasks**:
   - `update_time` is added using `self.add_update_func()` and runs periodically every `update_interval` milliseconds.
   - It updates the label asynchronously without freezing the GUI.
2. **Async Button Commands**:
   - `self.execute_async_command()` wraps an async function (`self.async_show_popup`) to be callable by a button.
3. **Async Popup**:
   - Clicking the button triggers an async function that shows a non-blocking popup window after a delay.

Run the code and enjoy a fully functional async GUI!

---

## Features

### 1. **Async Commands**
- Use `execute_async_command` to execute asynchronous functions when using the command keyword.
- Example:
  ```python
  button = ctk.CTkButton(self, text="Click me", command=self.execute_async_command(self.async_function))
  ```

### 2. **Periodic Background Updates**
- Schedule background update functions that run periodically without blocking the main GUI thread.
- Example:
  ```python
  self.add_update_func(update_func)
  ```

### 3. **Non-Blocking Async Mainloop**
- The custom mainloop integrates with `asyncio` and allows GUI updates, async background tasks, and async commands to run seamlessly in parallel.

---

## How It Works

### 1. **Async Mainloop**
- The `mainloop` method in `AsyncCTK` runs three parallel loops using `asyncio.gather()`:
   - **GUI Mainloop**: Handles `CustomTkinter` GUI events without blocking (see [insolor's async-tkinter-loop](https://github.com/insolor/async-tkinter-loop/tree/main))
   - **Command Loop**: Executes async commands placed into the commands queue (e.g., by buttons)
   - **Update Functions**: Runs user-defined periodic background tasks added via `add_update_func`

### 2. **Tweaks to the GUI Mainloop**
- The GUI mainloop has been rewritten based on [insolor's async-tkinter-loop](https://github.com/insolor/async-tkinter-loop/tree/main) to allow for the usage of asyncio.
- `self.dooneevent(_tkinter.DONT_WAIT)` is the key to allow the processing of events without freezing.

### 3. **Command Queue**
- Buttons and other widgets can't natively execute async functions.
- `execute_async_command` wraps an async function to an non-async function. Instead of executing the async function directly, the execution is scheduled for execution by adding it to the thread-safe command queue.
- Adding the command to the queue can be done in a non-async context, allowing widgets to execute async functions.
- The command queue is processed by the **Command Loop**.
- All commands are executed in parallel using `asyncio.gather`.

### 4. **Update Functions**
- Background tasks (e.g., updating a clock) are executed in parallel using `asyncio.gather`.
- A timeout ensures that no single task blocks the entire loop.
- The `update_interval` parameter controls the frequency of the background tasks.

---

## Known Issues

### Third-Party Libraries
Some third-party libraries may not be compatible with `AsyncCTK` due to their blocking nature. Most of them try to find the main thread and fail because the main loop is running in an asyncio loop.

---

## Credits
This project builds upon the foundation laid by [insolor's async-tkinter-loop](https://github.com/insolor/async-tkinter-loop), which provides tools for integrating `asyncio` with `Tkinter`.

While `async-tkinter-loop` focuses on providing async mainloop support, `AsyncCTK` expands the concept to:
- Allow periodic background tasks with proper management.

This library is a natural extension of the ideas but serves an extended purpose for developers needing fully-managed background task execution for large professional applications.

---

## License
This project is licensed under the **Apache 2.0 License**.

### What This Means:
- You are free to use, distribute, edit, and contribute to this code.
- Any modifications or contributions must also be distributed under the Apache 2.0 license.

### Note:
This license applies **only** to the code in this directory. External libraries or projects referenced (e.g., `CustomTkinter`, `async-tkinter-loop`) maintain their respective licenses.

---

## Contribute
Contributions are welcome! If you find bugs, need improvements, or have ideas for new features, feel free to open an issue or submit a pull request.
Sadly I dont have the time to maintain this as a pip package, but maybe in the future :). Would be nice to integrate it with [insolor's async-tkinter-loop](https://github.com/insolor/async-tkinter-loop) to have a more complete package with proper testing.

