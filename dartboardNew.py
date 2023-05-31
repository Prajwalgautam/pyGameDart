import cv2
import numpy as np
import pygame
from pygame.locals import *

# Initialize Pygame Zero
WIDTH = 800
HEIGHT = 600
TITLE = "AR Dart Board Game"
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

# Load the digital representation of a dart
dart_img = pygame.image.load('./img.png').convert_alpha()

# Define the dartboard detection parameters
lower_color = np.array([0, 100, 100])
upper_color = np.array([10, 255, 255])
dartboard_detected = False
dartboard_x, dartboard_y, dartboard_width, dartboard_height = 0, 0, 0, 0

# Game variables
score = 0
hand_pos = None

# Define the scoring areas and their respective points
scoring_areas = [
    {'name': 'Bullseye', 'points': 50, 'x_range': (0.4, 0.6), 'y_range': (0.4, 0.6)},
    {'name': 'Outer Ring', 'points': 25, 'x_range': (0.2, 0.8), 'y_range': (0.2, 0.8)},
    {'name': 'Inner Ring', 'points': 10, 'x_range': (0.3, 0.7), 'y_range': (0.3, 0.7)},
    {'name': 'Outer Area', 'points': 5, 'x_range': (0, 1), 'y_range': (0, 1)},
    {'name': 'Miss', 'points': 0, 'x_range': (0, 1), 'y_range': (0, 1)}
]

# Feedback messages based on the score
feedback_messages = {
    50: "Bullseye! Excellent shot!",
    25: "Great shot! You hit the outer ring!",
    10: "Nice shot! You hit the inner ring!",
    5: "Good shot! You hit the outer area.",
    0: "Missed the dartboard! Try again."
}

def calculate_score(hit_x, hit_y):
    for area in scoring_areas:
        x_range = area['x_range']
        y_range = area['y_range']
        if x_range[0] <= hit_x <= x_range[1] and y_range[0] <= hit_y <= y_range[1]:
            return area['points']
    return 0

def draw():
    screen.fill((0, 0, 0))  # Clear the screen
    if dartboard_detected:
        # Draw the dartboard overlay
        pygame.draw.rect(screen, (0, 255, 0), (dartboard_x, dartboard_y, dartboard_width, dartboard_height), 2)
    # Draw the dart image
    screen.blit(dart_img, (WIDTH // 2 - dart_img.get_width() // 2, HEIGHT - dart_img.get_height()))

    # Draw the score
    score_text = pygame.font.Font(None, 36).render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # Draw the hand or pointing device position
    if hand_pos is not None:
        pygame.draw.circle(screen, (255, 0, 0), hand_pos, 10)

    # Display feedback message based on the score
    feedback = feedback_messages.get(score, "")
    feedback_text = pygame.font.Font(None, 24).render(feedback, True, (255, 255, 255))
    screen.blit(feedback_text, (10, 50))

def on_mouse_down(pos):
    global score
    # Check if the dart image was clicked
    dart_rect = dart_img.get_rect()
    dart_rect.center = (WIDTH // 2, HEIGHT - dart_img.get_height() // 2)
    if dart_rect.collidepoint(pos):
        # Calculate the hit position relative to the dartboard region
        hit_x = (pos[0] - dartboard_x) / 500
        hit_y = (pos[1] - dartboard_y) / 500
        # Calculate the score based on the hit position
        score += calculate_score(hit_x, hit_y)

def update():
    global dartboard_detected, dartboard_x, dartboard_y, dartboard_width, dartboard_height
    global hand_pos
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Error capturing the frame")
        return

    # Convert the frame from BGR to HSV color space
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Apply color thresholding to isolate the dartboard
    mask = cv2.inRange(hsv_frame, lower_color, upper_color)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate over the contours and find the largest one
    max_area = 0
    max_contour = None
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
            max_contour = contour

    # Update dartboard detection variables
    if max_contour is not None and max_area > 500:
        x, y, w, h = cv2.boundingRect(max_contour)
        dartboard_x, dartboard_y, dartboard_width, dartboard_height = x, y, w, h
        dartboard_detected = True
    else:
        dartboard_detected = False

    # Find the hand or pointing device position
    if dartboard_detected:
        # Apply hand or pointing device tracking algorithm
        # Update hand_pos with the position of the hand or pointing device
        hand_landmarks = results.multi_hand_landmarks[0]  # Assuming only one hand is detected
        # Get the coordinates of a specific landmark (e.g., index finger tip)
        x = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * frame.shape[1])
        y = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * frame.shape[0])
        hand_pos = (x, y)
    else:
        hand_pos = None

# Create a VideoCapture object
cap = cv2.VideoCapture(0)  # 0 represents the default camera (you can change it if needed)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Unable to open the camera")
    exit()

# Start the Pygame Zero game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            cap.release()
            exit()
        elif event.type == MOUSEBUTTONDOWN:
            on_mouse_down(pygame.mouse.get_pos())

    update()
    draw()
    pygame.display.update()