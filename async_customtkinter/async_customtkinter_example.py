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
