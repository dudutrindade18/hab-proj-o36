import cv2

def show_webcam():
    # Initialize the webcam (0 is usually the built-in webcam)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        return
    
    print("Webcam is now active. Press 'q' to quit.")
    
    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Could not read frame.")
            break
        
        # Display the frame
        cv2.imshow('Webcam Feed', frame)
        
        # Check for 'q' key press to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    show_webcam() 