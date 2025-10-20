import cv2
import time
import os
import tkinter as tk
from PIL import Image, ImageTk
import threading
from utils.pose_landmarker import PoseLandmarker
from utils.hand_landmarker import HandLandmarker
from utils.custom_gesture_classifier import CustomGestureClassifier


class MotionPlayUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MotionPlay")
        self.root.geometry("1400x850")
        self.root.configure(bg='#f5f5f5')
        
        # Color scheme
        self.bg = '#f5f5f5'
        self.card = '#ffffff'
        self.accent = '#3b82f6'
        self.success = '#10b981'
        self.text = '#1f2937'
        self.text_light = '#6b7280'
        self.border = '#d1d5db'
        
        custom_model_path = 'custom_gesture_recognizer/gesture_classifier.pkl'
        self.use_custom_gesture = os.path.exists(custom_model_path)
        self.last_gesture = None
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0
        self.confidence_threshold = 0.7
        
        self.pose_detector = PoseLandmarker('models/pose_landmarker.task')
        
        if self.use_custom_gesture:
            self.gesture_classifier = CustomGestureClassifier(
                model_path=custom_model_path,
                hand_landmarker_path='models/hand_landmarker.task')
            self.hand_detector = None
        else:
            self.hand_detector = HandLandmarker('models/hand_landmarker.task')
            self.gesture_classifier = None
        
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.current_fps = 0
        self.fps_counter = 0
        self.fps_start_time = time.time()
        
        self.create_ui()
        self.start_camera()
        
    def create_ui(self):
        main = tk.Frame(self.root, bg=self.bg)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left side - Camera
        left = tk.Frame(main, bg=self.bg)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        cam_card = tk.Frame(left, bg=self.card, relief=tk.RIDGE, bd=1)
        cam_card.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(cam_card, text="Camera", font=("Arial", 14, "bold"),
                bg=self.card, fg=self.text).pack(anchor=tk.W, padx=15, pady=10)
        
        tk.Frame(cam_card, bg=self.border, height=1).pack(fill=tk.X, padx=15)
        
        canvas_frame = tk.Frame(cam_card, bg=self.card)
        canvas_frame.pack(padx=15, pady=15)
        
        self.canvas = tk.Canvas(canvas_frame, bg='#000', width=920, height=520,
                               highlightthickness=1, highlightbackground=self.border)
        self.canvas.pack()
        
        self.fps_label = tk.Label(cam_card, text="FPS: 0", font=("Arial", 10),
                                 bg=self.card, fg=self.text_light)
        self.fps_label.pack(anchor=tk.E, padx=15, pady=(0, 10))
        
        # Right side - Control panel
        right = tk.Frame(main, bg=self.bg)
        right.pack(side=tk.RIGHT, fill=tk.BOTH)
        right.configure(width=380)
        
        # Control buttons
        ctrl_card = tk.Frame(right, bg=self.card, relief=tk.RIDGE, bd=1)
        ctrl_card.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(ctrl_card, text="Control", font=("Arial", 12, "bold"),
                bg=self.card, fg=self.text).pack(anchor=tk.W, padx=15, pady=10)
        tk.Frame(ctrl_card, bg=self.border, height=1).pack(fill=tk.X, padx=15)
        
        self.btn = tk.Button(ctrl_card, text="PAUSE", command=self.toggle,
                            font=("Arial", 11, "bold"), bg=self.accent, fg=self.text_light,
                            relief=tk.FLAT, padx=35, pady=8, cursor='hand2',
                            activebackground='#2563eb', activeforeground=self.text_light)
        self.btn.pack(pady=15)
        
        # Status
        status_card = tk.Frame(right, bg=self.card, relief=tk.RIDGE, bd=1)
        status_card.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(status_card, text="Status", font=("Arial", 12, "bold"),
                bg=self.card, fg=self.text).pack(anchor=tk.W, padx=15, pady=10)
        tk.Frame(status_card, bg=self.border, height=1).pack(fill=tk.X, padx=15)
        
        s_frame = tk.Frame(status_card, bg=self.card)
        s_frame.pack(fill=tk.X, padx=15, pady=10)
        
        p_box = tk.Frame(s_frame, bg='#f3f4f6', padx=10, pady=6)
        p_box.pack(fill=tk.X, pady=(0, 6))
        tk.Label(p_box, text="Pose", font=("Arial", 9),
                bg='#f3f4f6', fg=self.text_light).pack(anchor=tk.W)
        self.pose_label = tk.Label(p_box, text="● Not Detected",
                                   font=("Arial", 9, "bold"),
                                   bg='#f3f4f6', fg=self.text_light)
        self.pose_label.pack(anchor=tk.W)
        
        h_box = tk.Frame(s_frame, bg='#f3f4f6', padx=10, pady=6)
        h_box.pack(fill=tk.X)
        txt = "Gesture" if self.use_custom_gesture else "Hand"
        tk.Label(h_box, text=txt, font=("Arial", 9),
                bg='#f3f4f6', fg=self.text_light).pack(anchor=tk.W)
        self.hand_label = tk.Label(h_box, text="● Not Detected",
                                   font=("Arial", 9, "bold"),
                                   bg='#f3f4f6', fg=self.text_light)
        self.hand_label.pack(anchor=tk.W)
        
        # Recognition results
        gest_card = tk.Frame(right, bg=self.card, relief=tk.RIDGE, bd=1)
        gest_card.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(gest_card, text="Recognition", font=("Arial", 12, "bold"),
                bg=self.card, fg=self.text).pack(anchor=tk.W, padx=15, pady=10)
        tk.Frame(gest_card, bg=self.border, height=1).pack(fill=tk.X, padx=15)
        
        g_box = tk.Frame(gest_card, bg='#f3f4f6', padx=15, pady=15)
        g_box.pack(fill=tk.X, padx=15, pady=10)
        
        self.gest_label = tk.Label(g_box, text="Waiting...",
                                   font=("Arial", 18, "bold"),
                                   bg='#f3f4f6', fg=self.text, wraplength=320)
        self.gest_label.pack()
        self.conf_label = tk.Label(g_box, text="Confidence: --",
                                   font=("Arial", 10),
                                   bg='#f3f4f6', fg=self.text_light)
        self.conf_label.pack(pady=(6, 0))
        
        # Text output
        out_card = tk.Frame(right, bg=self.card, relief=tk.RIDGE, bd=1)
        out_card.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(out_card, text="Output", font=("Arial", 12, "bold"),
                bg=self.card, fg=self.text).pack(anchor=tk.W, padx=15, pady=10)
        tk.Frame(out_card, bg=self.border, height=1).pack(fill=tk.X, padx=15)
        
        # Confidence threshold info
        info_frame = tk.Frame(out_card, bg='#fef3c7', padx=10, pady=8)
        info_frame.pack(fill=tk.X, padx=15, pady=(10, 0))
        tk.Label(info_frame, text=f"ℹ️ Text output only when confidence > {int(self.confidence_threshold * 100)}%",
                font=("Arial", 9), bg='#fef3c7', fg='#92400e', 
                wraplength=320, justify=tk.LEFT).pack(anchor=tk.W)
        
        txt_frame = tk.Frame(out_card, bg=self.card)
        txt_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        scroll = tk.Scrollbar(txt_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_out = tk.Text(txt_frame, height=5, font=("Courier", 11),
                                bg='#f3f4f6', fg=self.text, relief=tk.FLAT,
                                padx=8, pady=8, yscrollcommand=scroll.set)
        self.text_out.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.text_out.yview)
        
        tk.Button(out_card, text="Clear", command=self.clear,
                 font=("Arial", 9), bg='#6b7280', fg=self.text_light,
                 relief=tk.FLAT, padx=18, pady=5, cursor='hand2',
                 activebackground='#4b5563', activeforeground=self.text_light).pack(pady=(0, 10))
    
    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            return
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.is_running = True
        self.timestamp_ms = 0
        self.grab_count = 1
        threading.Thread(target=self.process, daemon=True).start()
        self.update_frame()
    
    def process(self):
        while self.is_running:
            if not self.cap or not self.cap.isOpened():
                break
            for _ in range(self.grab_count):
                self.cap.grab()
            ret, frame = self.cap.retrieve()
            if not ret:
                continue
            
            self.timestamp_ms += 33
            self.pose_detector.detect_async(frame, self.timestamp_ms)
            
            if self.use_custom_gesture:
                self.gesture_classifier.detect_async(frame, self.timestamp_ms)
                gestures = self.gesture_classifier.predict_gestures()
                t = time.time()
                if gestures:
                    g = gestures[0]['gesture']
                    c = gestures[0]['confidence']
                    h = gestures[0]['handedness']
                    self.root.after(0, self.update_gest, g, c, h)
                    if c > self.confidence_threshold:
                        if g != self.last_gesture or (t - self.last_gesture_time) > self.gesture_cooldown:
                            self.root.after(0, self.add_text, str(g))
                            self.last_gesture = g
                            self.last_gesture_time = t
                else:
                    self.root.after(0, self.update_gest, None, 0, "")
            else:
                self.hand_detector.detect_async(frame, self.timestamp_ms)
            
            frame = self.pose_detector.draw_landmarks_on_frame(frame)
            if self.use_custom_gesture:
                frame = self.gesture_classifier.draw_on_frame(frame)
            else:
                frame = self.hand_detector.draw_landmarks_on_frame(frame)
            frame = cv2.flip(frame, 1)
            
            pose_data = self.pose_detector.get_landmark_data()
            has_pose = pose_data and pose_data.pose_landmarks
            
            if self.use_custom_gesture:
                gestures = self.gesture_classifier.predict_gestures()
                num = len(gestures) if gestures else 0
            else:
                hand_data = self.hand_detector.get_landmark_data()
                num = len(hand_data.hand_landmarks) if hand_data and hand_data.hand_landmarks else 0
            
            self.root.after(0, self.update_status, has_pose, num)
            
            self.fps_counter += 1
            if time.time() - self.fps_start_time > 1.0:
                self.current_fps = self.fps_counter / (time.time() - self.fps_start_time)
                self.fps_counter = 0
                self.fps_start_time = time.time()
                self.grab_count = 1 if self.current_fps > 28 else (2 if self.current_fps > 25 else 3)
            
            self.current_frame = frame
    
    def update_frame(self):
        if self.current_frame is not None:
            rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            h, w = rgb.shape[:2]
            scale = min(920 / w, 520 / h)
            nw, nh = int(w * scale), int(h * scale)
            resized = cv2.resize(rgb, (nw, nh))
            img = ImageTk.PhotoImage(Image.fromarray(resized))
            self.canvas.delete("all")
            self.canvas.create_image((920 - nw) // 2, (520 - nh) // 2, anchor=tk.NW, image=img)
            self.canvas.image = img
            self.fps_label.config(text=f"FPS: {self.current_fps:.0f}")
        if self.is_running:
            self.root.after(30, self.update_frame)
    
    def update_status(self, pose, num):
        if pose:
            self.pose_label.config(text="● Detected", fg=self.success)
        else:
            self.pose_label.config(text="● Not Detected", fg=self.text_light)
        if num > 0:
            txt = f"● {num} gesture(s)" if self.use_custom_gesture else f"● {num} hand(s)"
            self.hand_label.config(text=txt, fg=self.success)
        else:
            self.hand_label.config(text="● Not Detected", fg=self.text_light)
    
    def update_gest(self, g, c, h):
        if g is not None:
            self.gest_label.config(text=f"{h}: {g}", fg=self.text)
            col = self.success if c > self.confidence_threshold else '#f59e0b'
            self.conf_label.config(text=f"Confidence: {c:.2%}", fg=col)
        else:
            self.gest_label.config(text="Waiting...", fg=self.text_light)
            self.conf_label.config(text="Confidence: --", fg=self.text_light)
    
    def add_text(self, txt):
        self.text_out.insert(tk.END, txt)
        self.text_out.see(tk.END)
    
    def clear(self):
        self.text_out.delete(1.0, tk.END)
    
    def toggle(self):
        if self.is_running:
            self.is_running = False
            self.btn.config(text="START", bg=self.success)
        else:
            self.is_running = True
            self.btn.config(text="PAUSE", bg=self.accent)
            threading.Thread(target=self.process, daemon=True).start()
            self.update_frame()
    
    def cleanup(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.pose_detector.release()
        if self.use_custom_gesture:
            self.gesture_classifier.release()
        else:
            self.hand_detector.release()


def main():
    root = tk.Tk()
    app = MotionPlayUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.cleanup(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
