import cv2

# Create a VideoCapture object
cap = cv2.VideoCapture(0)  # 0 represents the default camera (you can change it if needed)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Unable to open the camera")
    exit()

# Read and display the video frames
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Check if the frame was successfully captured
    if not ret:
        print("Error capturing the frame")
        break

    # Display the frame
    cv2.imshow("Video Feed", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close the windows
cap.release()
cv2.destroyAllWindows()
