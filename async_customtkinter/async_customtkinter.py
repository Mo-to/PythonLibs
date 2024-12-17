import asyncio
from collections.abc import Coroutine
from queue import Queue
from tkinter import TclError
from typing import Callable
import customtkinter as ctk
import _tkinter

class AsyncCTK(ctk.CTk):
    def __init__(self, update_interval: int = 1000):
        super().__init__()
        """ Update interval for the update function added by add_update_func """
        self._update_interval = update_interval

        """ List of update functions that are called every update_interval milliseconds """
        self._update_funcs = []

        """ Queue for commands scheduled by ctk elements """
        self.commands_queue = Queue()  # because command in buttons cant handle async functions, they should be added to this queue

        """ Set values needed for a working async mainloop """
        self._application_closed = False # needed for update_func_mainloop as well
        self._prepare_async()



    def _prepare_async(self):
        """
        Prepares the GUI for the async mainloop, heavily based on
        https://github.com/insolor/async-tkinter-loop/blob/main/examples/custom_tkinter.py
        https://github.com/insolor/async-tkinter-loop/blob/main/async_tkinter_loop/mixins.py

        Need to be edited to allow for custom background tasks added to the gui.async_eventloop()
        """
        self.deiconify()
        self._window_exists = True


    def add_update_func(self, update_func: Callable[[], Coroutine[None, None, None]]):
        """
        Adds an update function to the GUI. The update function is called every update_interval milliseconds.
        """
        self._update_funcs.append(update_func)


    def remove_update_func(self, update_func: Callable[[], Coroutine[None, None, None]]):
        """
        Removes an update function from the GUI.
        """
        self._update_funcs.remove(update_func)


    def execute_async_command(self, async_func: Callable[[], Coroutine[None, None, None]]) -> Callable[[], None]:
        """
        Returns a function that, when called, executes the async command
        by putting it into the commands queue.

        Usage Example:
            button = ctk.CTkButton(self, text="Click me", command=self.execute_async_command(self.async_show_popup))
            - Clicking the button will execute the async_show_popup function by putting it into the commands queue

        Parameters:
            async_func (Callable[[], Coroutine[None, None, None]]): The async function to be executed

        Returns:
            A non async Callable that puts the async function into the commands queue
        """
        def wrapper():
            nonlocal async_func
            command = asyncio.gather(
                async_func()
            )
            self.commands_queue.put(command, block=True)

        return wrapper


    async def mainloop(self):
        """
        Mainloop of the async customtkinter GUI

        Mainloop consists of three parallel loops:
        - GUI mainloop: Mainloop of the customtkinter GUI edited to work with async functions
        - Update function mainloop: Mainloop for the update functions added by add_update_func
        - Command mainloop: Mainloop to execute the commands in the commands queue, these are scheduled by the ctk elements using self.execute_async_command
        """
        await asyncio.gather(
            self._gui_mainloop(),  # Mainloop of tkinter
            self._update_func_mainloop(),  # Mainloop for the update functions
            self._command_mainloop()  # Update the page to be shown
        )


    async def _command_mainloop(self):
        """
        Loop that executes the commands in the commands queue, that are scheduled by the ctk elements
        """
        while True:
            if not self.commands_queue.empty():
                command = self.commands_queue.get()
                await command
            await asyncio.sleep(0.1) # Sleep to give parallel executions the chance to execute something else

    async def _gui_mainloop(self):
        """
        Edited mainloop of the ctk mainloop to allow async execution

        Heavily based on https://github.com/insolor/async-tkinter-loop/blob/main/async_tkinter_loop/async_tkinter_loop.py
        Credits to the original author of this code to give us the tools to finally have a working async tkinter mainloop
        """
        while True:
            while self.dooneevent(_tkinter.DONT_WAIT) > 0:
                pass

            try:
                self.winfo_exists()  # Will throw TclError if the main window is destroyed
            except TclError:
                break

            await asyncio.sleep(0.01)


    async def _update_func_mainloop(self):
        """
        Loop for the update_func defined in self._update_funcs by add_update_func

        All update functions are run in parallel using asyncio.gather. If not all update functions are finished within
        the update_interval, the function prints a warning message.
        """
        while True:
            coroutines = [update_func() for update_func in self._update_funcs]

            try:
                await asyncio.gather(
                    asyncio.wait_for(asyncio.gather(*coroutines), timeout=self._update_interval / 1000),
                    asyncio.sleep(self._update_interval / 1000) # ensure to wait at least update intervall
                )
            except asyncio.TimeoutError:
                print(f"AsyncCTK -> update -> Update func exceeded the allowed "
                      f"update intervall of {self._update_interval}ms.")

            if self._application_closed:
                break
