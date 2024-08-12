import os
import cv2
import gtuner
import time
import numpy as np
import threading

class GCVWorker:
    def __init__(self, width, height):
        os.chdir(os.path.dirname(__file__))
        self.gcvdata = bytearray([0x00, 0x00, 0x00, 0x00])
        self.perfect_throws_enabled = False
        self.quick_jukes_enabled = False
        self.last_toggle_time_perfect_throws = 0
        self.last_toggle_time_quick_jukes = 0
        self.debounce_delay = 0.5  # 500ms debounce delay
        self.show_instructions_flag = True
        self.instructions_thread = threading.Thread(target=self.show_instructions)
        self.instructions_thread.start()

    def __del__(self):
        del self.gcvdata

    def show_instructions(self):
        # Create a blank frame for instructions
        height, width = 480, 850
        instructions_frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Define the instructions text
        instructions = [
            "Instructions:",
            "1. Press Left Stick to toggle Perfect Throws.",
            "2. Press Right Stick to toggle Quick Jukes/Spins/Dead Leg.",
            "3. Use GPC to Modify Timing. Get timing down in MUT Practice Mode",
            "4. Do not release turbo when performing ballcarrier moves",
            "5. All modifiers will subtract from your original timing",
            "6. Discord: WhytePuma",
            "",
            "Press 'q' to close this window."
        ]

        # Define font and text properties
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        color = (255, 255, 255)  # White color

        # Put the instructions text on the frame
        y = 30
        for line in instructions:
            cv2.putText(instructions_frame, line, (10, y), font, font_scale, color, thickness)
            y += 40

        # Display the instructions frame until the user closes the window
        while self.show_instructions_flag:
            cv2.imshow("Instructions", instructions_frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.show_instructions_flag = False
            elif cv2.getWindowProperty("Instructions", cv2.WND_PROP_VISIBLE) < 1:
                self.show_instructions_flag = False

        cv2.destroyWindow("Instructions")

    def process(self, frame):
        current_time = time.time()

        # Toggle perfect throws
        if gtuner.get_actual(gtuner.BUTTON_9) and (
                current_time - self.last_toggle_time_perfect_throws) > self.debounce_delay:
            self.perfect_throws_enabled = not self.perfect_throws_enabled
            self.last_toggle_time_perfect_throws = current_time

        # Toggle quick jukes
        if gtuner.get_actual(gtuner.BUTTON_6) and (
                current_time - self.last_toggle_time_quick_jukes) > self.debounce_delay:
            self.quick_jukes_enabled = not self.quick_jukes_enabled
            self.last_toggle_time_quick_jukes = current_time

        # Update the gcvdata to reflect the states
        self.gcvdata[0] = 0x01 if self.perfect_throws_enabled else 0x00
        self.gcvdata[1] = 0x01 if self.quick_jukes_enabled else 0x00

        # Determine the text to display for perfect throws
        if self.perfect_throws_enabled:
            text1 = "Perfect Throws Enabled"
            color1 = (0, 255, 0)  # Green color
        else:
            text1 = "Perfect Throws Disabled"
            color1 = (0, 0, 255)  # Red color

        # Determine the text to display for quick jukes
        if self.quick_jukes_enabled:
            text2 = "Quick Jukes Enabled"
            color2 = (0, 255, 0)  # Green color
        else:
            text2 = "Quick Jukes Disabled"
            color2 = (0, 0, 255)  # Red color

        # Get the frame dimensions
        height, width, _ = frame.shape

        # Define the font and size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2

        # Calculate the position for the text
        text_size1 = cv2.getTextSize(text1, font, font_scale, thickness)[0]
        text_size2 = cv2.getTextSize(text2, font, font_scale, thickness)[0]
        text_x1 = width - text_size1[0] - 10
        text_x2 = width - text_size2[0] - 10
        text_y1 = 30
        text_y2 = 60

        # Put the text on the frame
        cv2.putText(frame, text1, (text_x1, text_y1), font, font_scale, color1, thickness)
        cv2.putText(frame, text2, (text_x2, text_y2), font, font_scale, color2, thickness)

        return frame, self.gcvdata
