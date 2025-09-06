import cv2
import numpy as np
import os

def rotate_image(image_path, angle):
    """
    หมุนรูปภาพตามองศาที่กำหนดและตัดขอบดำออก
    """
    # อ่านรูปภาพ
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("ไม่สามารถอ่านรูปภาพได้")
    
    # หาจุดกึ่งกลางของรูป
    height, width = img.shape[:2]
    center = (width // 2, height // 2)
    
    # สร้าง rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # คำนวณขนาดใหม่หลังหมุนเพื่อไม่ให้รูปถูกตัด
    cos = np.abs(rotation_matrix[0, 0])
    sin = np.abs(rotation_matrix[0, 1])
    new_width = int((height * sin) + (width * cos))
    new_height = int((height * cos) + (width * sin))
    
    # ปรับ rotation matrix ให้รูปอยู่กึ่งกลาง
    rotation_matrix[0, 2] += (new_width / 2) - center[0]
    rotation_matrix[1, 2] += (new_height / 2) - center[1]
    
    # หมุนรูปภาพด้วยขนาดใหม่
    rotated_img = cv2.warpAffine(img, rotation_matrix, (new_width, new_height), 
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    
    # ตัดขอบดำออก
    cropped_img = crop_black_borders(rotated_img)
    
    return cropped_img

def crop_black_borders(image):
    """
    ตัดขอบดำออกจากรูปภาพ
    """
    # แปลงเป็น grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # หาพิกัดที่ไม่ใช่สีดำ (threshold = 10 เพื่อให้ยืดหยุ่น)
    coords = cv2.findNonZero((gray > 10).astype(np.uint8))
    
    if coords is not None:
        # หา bounding box ของพื้นที่ที่ไม่ใช่สีดำ
        x, y, w, h = cv2.boundingRect(coords)
        
        # ตัดรูปตาม bounding box พร้อมเพิ่ม padding เล็กน้อย
        padding = 5
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(image.shape[1] - x, w + 2 * padding)
        h = min(image.shape[0] - y, h + 2 * padding)
        
        cropped = image[y:y+h, x:x+w]
        return cropped
    else:
        # หากไม่พบพื้นที่ที่ไม่ใช่สีดำ ให้คืนรูปต้นฉบับ
        return image

def create_rotated_images(image_path):
    """
    หมุนรูปภาพทีละ 5 องศา จาก -45 ถึง +45 องศา
    บันทึกแยกออกมาเป็นไฟล์ละ 1 รูป
    """
    # ตรวจสอบว่าไฟล์รูปมีอยู่จริง
    if not os.path.exists(image_path):
        raise ValueError(f"ไม่พบไฟล์รูปภาพ: {image_path}")
    
    # หาโฟลเดอร์และชื่อไฟล์
    output_dir = os.path.dirname(image_path)
    if not output_dir:
        output_dir = "."  # ใช้โฟลเดอร์ปัจจุบันถ้าไม่มี path
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    print(f"เริ่มประมวลผลรูป: {os.path.basename(image_path)}")
    print(f"บันทึกไฟล์ไปที่: {output_dir}")
    print("=" * 50)
    
    # เก็บรายชื่อไฟล์ที่สร้าง
    created_files = []
    
    # หมุนรูปจาก -45 ถึง +45 องศา ทีละ 5 องศา
    for angle in range(-45, 50, 5):  # -45 ถึง 45 ทีละ 5
        try:
            # หมุนรูปภาพและตัดขอบดำ
            rotated_img = rotate_image(image_path, angle)
            
            # สร้างชื่อไฟล์ใหม่ (มีทั้งลบและบวก)
            new_filename = f"{base_name}.{angle}.jpg"
            output_path = os.path.join(output_dir, new_filename)
            
            # บันทึกรูปหมุน
            success = cv2.imwrite(output_path, rotated_img)
            
            if success:
                created_files.append(new_filename)
                print(f"✓ หมุน {angle:+3d}° → {new_filename}")
            else:
                print(f"✗ บันทึกไฟล์ {new_filename} ไม่สำเร็จ")
                
        except Exception as e:
            print(f"✗ เกิดข้อผิดพลาดในการหมุนรูป {angle}°: {e}")
    
    print("=" * 50)
    print(f"สร้างรูปภาพสำเร็จ: {len(created_files)}/{len(range(-45, 50, 5))} ไฟล์")
    print("\nรายชื่อไฟล์ที่สร้าง:")
    for filename in created_files:
        print(f"  📁 {filename}")
    
    return created_files

def create_sample_image():
    """
    สร้างรูปมือตัวอย่างสำหรับทดสอบ
    """
    # สร้างรูปภาพตัวอย่าง
    img = np.ones((400, 300, 3), dtype=np.uint8) * 255  # พื้นหลังสีขาว
    
    # วาดรูปมือแบบง่าย
    # ฝ่ามือ
    cv2.ellipse(img, (150, 250), (60, 80), 0, 0, 360, (255, 200, 150), -1)
    
    # นิ้วโป้ง
    cv2.ellipse(img, (110, 200), (15, 35), -30, 0, 360, (255, 200, 150), -1)
    
    # นิ้วชี้
    cv2.rectangle(img, (130, 140), (150, 200), (255, 200, 150), -1)
    cv2.ellipse(img, (140, 140), (10, 15), 0, 0, 360, (255, 200, 150), -1)
    
    # นิ้วกลาง
    cv2.rectangle(img, (150, 120), (170, 200), (255, 200, 150), -1)
    cv2.ellipse(img, (160, 120), (10, 15), 0, 0, 360, (255, 200, 150), -1)
    
    # นิ้วนาง
    cv2.rectangle(img, (170, 140), (190, 200), (255, 200, 150), -1)
    cv2.ellipse(img, (180, 140), (10, 15), 0, 0, 360, (255, 200, 150), -1)
    
    # นิ้วก้อย
    cv2.rectangle(img, (190, 160), (210, 200), (255, 200, 150), -1)
    cv2.ellipse(img, (200, 160), (10, 15), 0, 0, 360, (255, 200, 150), -1)
    
    # เพิ่มขอบมือ
    cv2.ellipse(img, (150, 250), (60, 80), 0, 0, 360, (200, 150, 100), 3)
    
    # เพิ่มข้อความ
    cv2.putText(img, 'HAND SAMPLE', (80, 350), cv2.FONT_HERSHEY_SIMPLEX, 
                0.8, (0, 0, 0), 2, cv2.LINE_AA)
    
    # บันทึกรูป
    cv2.imwrite('Hand_0011336.jpg', img)
    return 'Hand_0011336.jpg'

# วิธีใช้งาน
if __name__ == "__main__":
    # ใช้รูปภาพที่คุณระบุ
    image_path = r"C:\Users\PC\Downloads\45-45\image1068_jpg.rf.195fdd7d4a598c5975231c0e890683b1.jpg"
    
    # เช็คว่าไฟล์รูปมีอยู่จริงหรือไม่
    if not os.path.exists(image_path):
        print(f"ไม่พบไฟล์รูปภาพ: {image_path}")
        print("กำลังสร้างรูปภาพมือตัวอย่างแทน...")
        # สร้างรูปภาพมือตัวอย่าง หากไม่พบไฟล์
        sample_image = create_sample_image()
        image_path = "Hand_0011336.jpg"
        print("สร้างรูปภาพมือตัวอย่างแล้ว: Hand_0011336.jpg")
    else:
        print(f"พบไฟล์รูปภาพ: {os.path.basename(image_path)}")
    
    try:
        created_files = create_rotated_images(image_path)
        print(f"\n🎉 เสร็จสิ้นการประมวลผล! สร้างรูป {len(created_files)} ไฟล์")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        print("\nกรุณาตรวจสอบ:")
        print("1. ว่าไฟล์รูปภาพมีอยู่จริง")
        print("2. ว่าติดตั้ง opencv-python และ numpy แล้ว")
        print("3. ว่ามีสิทธิ์ในการเขียนไฟล์ในโฟลเดอร์นี้")
