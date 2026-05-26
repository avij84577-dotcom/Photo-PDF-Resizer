import os
from flask import Flask, render_template, request, send_file
from PIL import Image
import io

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/resize', methods=['POST'])
def resize_image():
    if 'photo' not in request.files:
        return "কোনো ছবি সিলেক্ট করা হয়নি!", 400
    
    file = request.files['photo']
    if file.filename == '':
        return "কোনো ছবি সিলেক্ট করা হয়নি!", 400

    target_size_kb = int(request.form.get('size_kb', 50))
    target_size_bytes = target_size_kb * 1024

    img = Image.open(file.stream)
    
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # প্রথম চেষ্টা: শুধু কোয়ালিটি কমিয়ে সাইজ ছোট করা
    quality = 90
    output = io.BytesIO()
    
    while quality > 10:
        output.seek(0)
        output.truncate(0)
        img.save(output, format="JPEG", quality=quality)
        if output.tell() <= target_size_bytes:
            break
        quality -= 5

    # দ্বিতীয় চেষ্টা: যদি কোয়ালিটি কমানোর পরেও সাইজ বড় থাকে, তবে ছবির ডাইমেনশন (Resolution) ছোট করা হবে
    if output.tell() > target_size_bytes:
        # ছবির আসল সাইজ কত তা দেখা
        width, height = img.size
        scale_factor = 0.9 # প্রতিবারে ১০% করে ছবি ছোট করা হবে
        
        while output.tell() > target_size_bytes and width > 100:
            width = int(width * scale_factor)
            height = int(height * scale_factor)
            
            # ছবিটিকে নতুন সাইজে রিসাইজ করা
            resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            output.seek(0)
            output.truncate(0)
            resized_img.save(output, format="JPEG", quality=40) # ফিক্সড ভালো কোয়ালিটি

    output.seek(0)
    
    return send_file(
        output,
        mimetype='image/jpeg',
        as_attachment=True,
        download_name=f"resized_{file.filename.split('.')[0]}.jpg"
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)