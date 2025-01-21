
import cv2
import mediapipe as mp
import pyautogui
import random
import numpy as np

class HandGestureController:
    def __init__(self):
        # Disable PyAutoGUI failsafe
        pyautogui.FAILSAFE = False

        # Screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()

        # Mediapipe hands setup
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            max_num_hands=1
        )
        self.draw = mp.solutions.drawing_utils

    def get_angle(self, a, b, c):
        """Calculate angle between three points"""
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(np.degrees(radians))
        return angle

    def get_distance(self, landmark_list):
        """Calculate distance between two points"""
        if len(landmark_list) < 2:
            return 0
        (x1, y1), (x2, y2) = landmark_list[0], landmark_list[1]
        L = np.hypot(x2 - x1, y2 - y1)
        return np.interp(L, [0, 1], [0, 1000])

    def find_finger_tip(self, processed):
        """Find the tip of the index finger"""
        if processed.multi_hand_landmarks:
            hand_landmarks = processed.multi_hand_landmarks[0]
            index_finger_tip = hand_landmarks.landmark[self.mpHands.HandLandmark.INDEX_FINGER_TIP]
            return index_finger_tip
        return None

    def move_mouse(self, index_finger_tip):
        """Move mouse based on finger tip position"""
        if index_finger_tip is not None:
            x = int(index_finger_tip.x * self.screen_width * 2.4)
            y = int(index_finger_tip.y / 2 * self.screen_height * 2.4)
            
            # Apply fine-tuning factors
            x = int(x * 1.1)
            y = int(y * 1.1)
            pyautogui.moveTo(x, y)

    def is_left_click(self, landmark_list, thumb_index_dist):
        """Detect left click gesture"""
        return (
            self.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and
            self.get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) > 90 and
            thumb_index_dist > 50
        )

    def is_right_click(self, landmark_list, thumb_index_dist):
        """Detect right click gesture"""
        return (
            self.get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50 and
            self.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) > 90 and
            thumb_index_dist > 50
        )

    def is_double_click(self, landmark_list, thumb_index_dist):
        """Detect double click gesture"""
        return (
            self.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and
            self.get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50 and
            thumb_index_dist > 50
        )

    def is_screenshot(self, landmark_list, thumb_index_dist):
        """Detect screenshot gesture"""
        return (
            self.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) < 50 and
            self.get_angle(landmark_list[9], landmark_list[10], landmark_list[12]) < 50 and
            thumb_index_dist < 50
        )

    def detect_gesture(self, frame, landmark_list, processed):
        """Detect and execute hand gestures"""
        if len(landmark_list) >= 21:
            index_finger_tip = self.find_finger_tip(processed)
            thumb_index_dist = self.get_distance([landmark_list[4], landmark_list[5]])

            # Cursor movement
            if self.get_distance([landmark_list[4], landmark_list[5]]) < 50 and                self.get_angle(landmark_list[5], landmark_list[6], landmark_list[8]) > 90:
                self.move_mouse(index_finger_tip)
            
            # Left Click
            elif self.is_left_click(landmark_list, thumb_index_dist):
                pyautogui.click()
                cv2.putText(frame, "Left Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Right Click
            elif self.is_right_click(landmark_list, thumb_index_dist):
                pyautogui.rightClick()
                cv2.putText(frame, "Right Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Double Click
            elif self.is_double_click(landmark_list, thumb_index_dist):
                pyautogui.doubleClick()
                cv2.putText(frame, "Double Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            
            # Screenshot
            elif self.is_screenshot(landmark_list, thumb_index_dist):
                im1 = pyautogui.screenshot()
                label = random.randint(1, 1000)
                im1.save(f'my_screenshot_{label}.png')
                cv2.putText(frame, "Screenshot Taken", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    def run(self):
        """Main method to run hand gesture control"""
        cap = cv2.VideoCapture(0)

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Flip and convert frame
                frame = cv2.flip(frame, 1)
                frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process hand landmarks
                processed = self.hands.process(frameRGB)

                landmark_list = []
                if processed.multi_hand_landmarks:
                    hand_landmarks = processed.multi_hand_landmarks[0]
                    self.draw.draw_landmarks(frame, hand_landmarks, self.mpHands.HAND_CONNECTIONS)
                    
                    for lm in hand_landmarks.landmark:
                        landmark_list.append((lm.x, lm.y))

                # Detect and execute gestures
                self.detect_gesture(frame, landmark_list, processed)

                # Display frame
                cv2.imshow('Hand Gesture Control', frame)
                
                # Exit on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        finally:
            # Cleanup
            cap.release()
            cv2.destroyAllWindows()

def main():
    controller = HandGestureController()
    controller.run()

if __name__ == '__main__':
    main()
