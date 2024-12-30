import cv2 # pip install opencv-python
import configuration
import displayprovider
import pyxel

# Open webcam

class App:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.fdd = displayprovider.get_display()
        pyxel.init(configuration.WIDTH, configuration.HEIGHT, fps=60)
        pyxel.run(self.update, self.draw)

    def update(self):
        ...

    def draw(self):        
        # Capture frame-by-frame
        ret, frame = self.cap.read()

        # flip frame vertically
        frame = cv2.flip(frame, 1)

        # Check if frame is captured successfully
        if not ret:
            print("Failed to capture frame")

        resized_frame = cv2.resize(frame, (configuration.WIDTH, configuration.HEIGHT))

        # Convert the frame to grayscale
        gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur
        gray_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

        # Apply binary thresholding
        _, bw_frame = cv2.threshold(gray_frame, 127, 255, cv2.THRESH_BINARY)

        # Iterate over each pixel and send to filipdotdisplay
        self.fdd.clear()
        pyxel.cls(0)
        for y in range(configuration.HEIGHT):
            for x in range(configuration.WIDTH):
                pixel_value = bw_frame[y, x]
                self.fdd.px(x, y, pixel_value != 0)
                pyxel.pset(x, y, 7 if pixel_value != 0 else 0)
        self.fdd.show()

        # Display the resulting frame
        cv2.imshow('Webcam', gray_frame)

        # Release the capture and close windows
        #cap.release()
        #cv2.destroyAllWindows()


if __name__ == "__main__":
    App()
