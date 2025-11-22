import subprocess
import os
import sys

def convert_video(input_path, output_path=None, height=720, fps=25, quality=23):
    """
    Convert video to specified resolution and frame rate using FFmpeg.
    
    Args:
        input_path (str): Path to input video file
        output_path (str): Path for output video file (optional)
        height (int): Target height in pixels (default: 720)
        fps (int): Target frame rate (default: 25)
        quality (int): CRF quality value 0-51, lower is better (default: 23)
    
    Returns:
        bool: True if conversion successful, False otherwise
    """
    
    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return False
    
    # Generate output filename if not provided
    if output_path is None:
        name, ext = os.path.splitext(input_path)
        output_path = f"{name}_720p_{fps}fps{ext}"
    
    # Check if FFmpeg is available
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: FFmpeg not found. Please install FFmpeg and add it to your PATH.")
        return False
    
    cmd = [
        "ffmpeg",
        "-i", input_path,             # input file
        "-vf", f"scale=-1:{height}",  # scale maintaining aspect ratio
        "-r", str(fps),               # frame rate
        "-c:v", "libx264",            # video codec
        "-c:a", "aac",                # audio codec
        "-b:a", "128k",               # audio bitrate
        "-preset", "medium",          # encoding speed
        "-crf", str(quality),         # quality (lower = better)
        "-y",                         # overwrite output file if exists
        output_path
    ]
    
    try:
        print(f"Converting '{input_path}' to '{output_path}'...")
        print(f"Target: {height}p @ {fps}fps (quality: {quality})")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Conversion completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        print(f"FFmpeg stderr: {e.stderr}")
        return False

def main():
    """Main function to run the video converter."""
    
    # Default settings
    input_path = "input.mp4"
    output_path = "output_720p_25fps.mp4"
    
    # You can modify these parameters as needed
    height = 720      # Target height in pixels
    fps = 25          # Target frame rate
    quality = 23      # CRF quality (0-51, lower is better)
    
    # Convert the video
    success = convert_video(input_path, output_path, height, fps, quality)
    
    if success:
        print(f"Output saved as: {output_path}")
    else:
        print("Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
