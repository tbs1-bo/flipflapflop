import cv2 # pip install opencv-python
import configuration
import displayprovider

# Open webcam

def main():
    cap = cv2.VideoCapture(0)
    fdd = displayprovider.get_display()
    
    while True :
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Check if frame is captured successfully
        if not ret:
            print("Failed to capture frame")
            break

        #resized_frame = cv2.resize(frame, (configuration.WIDTH, configuration.HEIGHT))

        # Crop the frame
        height, width = frame.shape[:2]
        start_x = 0
        start_y = 0
        end_x = start_x + configuration.WIDTH
        end_y = start_y + configuration.HEIGHT
        cropped_frame = frame[start_y:end_y, start_x:end_x]

        # Convert the frame to grayscale
        gray_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)

        # Apply binary thresholding
        _, bw_frame = cv2.threshold(gray_frame, 100, 255, cv2.THRESH_BINARY)

        # Iterate over each pixel and send to filipdotdisplay
        fdd.clear()
        for y in range(configuration.HEIGHT):
            for x in range(configuration.WIDTH):
                pixel_value = bw_frame[y, x]
                fdd.px(x, y, pixel_value != 0)
        fdd.show()

        # Display the resulting frame
        cv2.imshow('Webcam', cropped_frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
